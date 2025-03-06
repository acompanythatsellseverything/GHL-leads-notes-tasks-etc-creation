import os
import logging
import traceback
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from utils.create_lead import create_ghl_lead
from utils.update_lead import _update_lead
from utils.slack_troubleshooting import send_slack_notification
from utils.utils import _get_lead_by_email

app = Flask(__name__)

load_dotenv()

API_KEY = os.getenv("FLASK_API_KEY")

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
        lead = create_ghl_lead(request.json)

        if not lead.get("contact"):
            logger.info(f"User was not created\n{lead}")
            return jsonify({"error": f"User was not created\n{lead}"}), 200

        logger.info(f"User was created\n{lead}")
        return jsonify({"Lead successfully created": f"{lead}"}), 201

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
    logger.info(f"Received lead request with such payload:\n{request.json}")
    # end auth block _____________________________________________

    # update lead block ____________________________________________
    try:
        updated_lead = _update_lead(request.json, lead_id)
        if not updated_lead.get("contact"):
            logger.info(f"User was not updated\n{updated_lead}")
            return jsonify({"error": f"User was not updated\n{updated_lead}"}), 200

        logger.info(f"User was updated\n{updated_lead}")
        return jsonify({"Lead successfully updated": f"{updated_lead}"}), 201
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
    lead_email = request.json.get("email")
    ghl_id = _get_lead_by_email(lead_email)
    if ghl_id is False:
        return jsonify({"message": f"There is no such contact with email = {lead_email}"}), 200
    return jsonify({"lead_id": ghl_id}), 200


@app.route('/note', methods=['POST'])
def create_note():
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"notes": "under development"}), 200


@app.route('/task', methods=['POST'])
def create_task():
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"tasks": "under development"}), 200


if __name__ == '__main__':
    app.run()
