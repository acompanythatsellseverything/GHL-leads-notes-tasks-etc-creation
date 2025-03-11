import os
import logging
import traceback
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, render_template, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
from marshmallow import ValidationError

from utils.add_tags import add_tags
from utils.create_lead import create_ghl_lead
from utils.update_lead import _update_lead
from utils.slack_troubleshooting import send_slack_notification
from utils.utils import _get_lead_by_email, _get_user_by_email
from validation.get_lead_validation import get_lead_by_email_schema
from validation.create_lead_validation import PostLeadSchema, post_lead_schema
from validation.update_lead_validation import update_lead_schema

app = Flask(__name__)

load_dotenv()

API_KEY = os.getenv("FLASK_API_KEY")

# Swagger
SWAGGER_URL = "/swagger"
API_DOCS = "/static/swagger.json"
swagger_ui = get_swaggerui_blueprint(SWAGGER_URL, API_DOCS)
app.register_blueprint(swagger_ui, url_prefix=SWAGGER_URL)

# Ensure the logs directory exists
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Log file path
log_file = os.path.join(log_directory, "app.log")

# Set up file logging (rotating logs daily)
file_handler = TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)

# Set up console logging (for terminal output)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)

# Get the root logger and configure it
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


@app.route('/')
def index():
    logger.debug("Home route accessed")
    return render_template("index.html")


@app.route('/lead', methods=['POST'])
def create_lead():

    # auth block ______________________________________________
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received lead request with such payload:\n{request.json}")
    # end auth block _____________________________________________

    # create lead block _______________________________________
    try:
        validated_data = post_lead_schema.load(request.json)

        lead = create_ghl_lead(validated_data)

        if not lead.get("contact"):
            logger.info(f"User was not created\n{lead}")
            return jsonify({"error": f"User was not created\n{lead}"}), 200

        logger.info(f"User was created\n{lead}")
        return jsonify({"Lead successfully created": f"{lead}"}), 201

    except ValidationError as err:
        send_slack_notification("Validation Error while creating lead\n" + str(err))
        return jsonify({"validation error": err.messages}), 400

    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while creating lead\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while creating lead\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"error: {e}"}), 400
    # end create lead block ___________________________________________


@app.route('/lead/<string:lead_id>', methods=['PUT'])
def update_lead(lead_id):

    # auth block ______________________________________________
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received lead update request with such payload:\n{request.json}")
    # end auth block _____________________________________________

    # update lead block ____________________________________________
    try:
        validated_data = update_lead_schema.load(request.json)
        updated_lead = _update_lead(validated_data, lead_id)
        if not updated_lead.get("contact"):
            logger.info(f"User was not updated\n{updated_lead}")
            return jsonify({"error": f"User was not updated\n{updated_lead}"}), 200

        logger.info(f"User was updated\n{updated_lead}")
        return jsonify({"Lead successfully updated": f"{updated_lead}"}), 201
    except ValidationError as err:
        send_slack_notification("Validation Error while updating lead\n" + str(err))
        logger.error("Validation Error while updating lead\n" + str(err))
        return jsonify({"validation error while updating lead": err.messages}), 400
    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while updating lead\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while updating lead\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"error: {e}"}), 400
    # end update lead block ______________________________


@app.route('/get_lead', methods=['POST'])
def get_lead_by_email():
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received payload for lead lookup {request.json}")
    try:
        validated_data = get_lead_by_email_schema.load(request.json)
    except ValidationError as err:
        send_slack_notification("Validation Error while getting lead\n" + str(err))
        logger.error("Validation Error while getting lead\n" + str(err))
        return jsonify({"validation error": err.messages}), 400
    lead_email = validated_data.get("email")
    ghl_id = _get_lead_by_email(lead_email)
    if ghl_id is False:
        return jsonify({"message": f"There is no such contact with email = {lead_email}"}), 200
    return jsonify({"lead_id": ghl_id}), 200


@app.route('/get_user', methods=['POST'])
def get_user_by_email():
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received payload for user lookup {request.json}")
    try:
        lookup_email = request.json.get("email")
        team_member_id = _get_user_by_email(lookup_email)
    except ValidationError as err:
        send_slack_notification("Validation Error while getting lead\n" + str(err))
        logger.error("Validation Error while getting lead\n" + str(err))
        return jsonify({"validation error": err.messages}), 400
    if team_member_id is False:
        return jsonify({"message": f"There is no such user with email = {lookup_email}"}), 200
    return jsonify({"user_id": team_member_id}), 200


@app.route('/lead/<string:lead_id>/tags', methods=['PATCH'])
def add_tag_to_lead(lead_id):
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received tags payload:\n{request.json}")

    try:
        lead = add_tags(ghl_id=lead_id, tags_to_add=request.json)
        logger.info("Tags added successfully")
        return jsonify({"data": lead})

    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while adding tags\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while adding tags\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"error: {e}"}), 400


@app.route('/task', methods=['POST'])
def create_task():
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"tasks": "under development"}), 200


if __name__ == '__main__':
    app.run()
