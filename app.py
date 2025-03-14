import logging
import os
import traceback
from logger import logger
from flask import Flask, render_template, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
from marshmallow import ValidationError

from utils.add_tags import add_tags
from utils.create_lead import create_ghl_lead
from utils.create_note import create_lead_property_inquiry
from utils.create_tasks import create_task
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


@app.route("/health")
def health():
    return "Healthy", 200


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
        #  Validate data and check if property is in payload
        validated_data = post_lead_schema.load(request.json)
        has_property = 'property' in validated_data

        lead = create_ghl_lead(validated_data, has_property)

        if not lead.get("contact"):
            logger.info(f"User was not created\n{lead}")
            return jsonify({"message": f"User was not created", "contact": lead}), 200

        logger.info(f"User was created\n{lead}")
        return jsonify(
            {
                "message": "Lead successfully created",
                "contact": lead.get("contact")
            }
        ), 201

    except ValidationError as err:  # Handling Validation Error
        send_slack_notification("Validation Error while creating lead\n" + str(err))
        logger.error("Validation Error while creating lead\n" + str(err))
        return jsonify({"validation error": err.messages}), 400

    except Exception as e:  # Handling any other Error
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
        return jsonify({"Lead successfully updated": f"{updated_lead}"}), 200
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
        lead_email = validated_data.get("email")
        lead = _get_lead_by_email(lead_email)
    except ValidationError as err:
        send_slack_notification("Validation Error while getting lead\n" + str(err))
        logger.error("Validation Error while getting lead\n" + str(err))
        return jsonify({"validation error": err.messages}), 400
    except Exception as e:
        send_slack_notification("Error while getting lead\n" + str(e))
        logger.error("Error while getting lead\n" + str(e))
        return jsonify({"Error while getting lead\n": e}), 400
    if lead is False:
        return jsonify({"message": f"There is no such contact with email = {lead_email}"}), 200
    return jsonify({"lead": lead}), 200


@app.route('/get_user', methods=['POST'])
def get_user_by_email():
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received payload for user lookup {request.json}")
    try:
        lookup_email = request.json.get("email")
        team_member = _get_user_by_email(lookup_email)
    except ValidationError as err:
        send_slack_notification("Validation Error while getting lead\n" + str(err))
        logger.error("Validation Error while getting lead\n" + str(err))
        return jsonify({"validation error": err.messages}), 400
    except Exception as e:
        send_slack_notification("Error while getting lead\n" + str(e))
        logger.error("Error while getting a user\n" + str(e))
        return jsonify({"Error while getting a user\n": e}), 400
    if team_member is False:
        return jsonify({"message": f"There is no such user with email = {lookup_email}"}), 200
    return jsonify({"user": team_member}), 200


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


@app.route('/lead/<string:lead_id>/notes', methods=['POST'])
def add_notes_to_lead(lead_id):
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received notes payload:\n{request.json}")

    try:
        lead = create_lead_property_inquiry(ghl_id=lead_id, data=request.json)
        logger.info("Note added successfully")
        return jsonify({"data": lead}), 201

    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while adding tags\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while adding tags\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"error: {e}"}), 400


@app.route('/lead/<string:lead_id>/tasks', methods=['POST'])
def create_task_endpoint(lead_id):
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    logger.info(f"Received task payload:\n{request.json}")
    try:
        lead_task = create_task(lead_id, request.json)
    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while adding task\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while adding task\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"error: {e}"}), 400
    return jsonify({"tasks": lead_task}), 200


if __name__ == '__main__':
    logger.info("Starting app")
    app.run()
