import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from utils.create_lead import create_ghl_lead

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
def index():  # put application's code here
    logger.debug("Home route accessed")
    return render_template("index.html")


@app.route('/lead', methods=['POST'])
def create_lead():
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received lead request with such payload:\n{request.json}")
    #try: # TODO uncomment these
    lead = create_ghl_lead(request.json)

    if not lead.get("contact"):
        logger.info(f"User was not created\n{lead}")
        return jsonify({"error": f"User was not created\n{lead}"}), 405

    return jsonify({"Lead successfully created": f"{lead}"}), 201
    # except Exception as e:
    #     logger.error(f"Error while creating a lead {e}")
    #     return jsonify({"message": f"error: {e}"}), 405

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
