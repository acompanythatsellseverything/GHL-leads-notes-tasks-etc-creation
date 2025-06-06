import os
import traceback

from db.ponds_query import get_ponds
from logger import logger
from flask import Flask, render_template, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
from marshmallow import ValidationError

from utils.add_tags import add_tags
from utils.create_lead import create_ghl_lead
from utils.create_note import create_lead_property_inquiry
from utils.create_tasks import create_task
from utils.delete_lead import _delete_lead
from utils.update_lead import _update_lead, add_followers
from utils.slack_troubleshooting import send_slack_notification
from utils.utils import _get_lead_by_email, _get_user_by_email, _get_lead_by_id, _get_users_list, _get_user_by_id
from validation.add_tags_validation import tags_validation
from validation.followers_validation import followers_schema
from validation.get_lead_validation import get_lead_by_email_schema
from validation.create_lead_validation import post_lead_schema
from validation.notes_validation import notes_validation
from validation.task_validation import task_validation
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

        if not lead:
            logger.info(f"User was not created\n{lead}")
            return jsonify({"message": f"User was not created, already exists. Added inquiry note if provided", "contact": lead}), 200

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
        return jsonify({"message": f"Validation error {err.messages}", "contact": None}), 406

    except Exception as e:  # Handling any other Error
        error_msg = traceback.format_exc()
        send_slack_notification("Error while creating lead\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while creating lead\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"error: {e}", "contact": None}), 400
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
        logger.info(f"{updated_lead}")
        if not updated_lead:
            logger.info(f"User was not updated")
            return jsonify({"message": f"User was not updated", "contact": None}), 202
    except ValidationError as err:
        send_slack_notification("Validation Error while updating lead\n" + str(err))
        logger.error("Validation Error while updating lead\n" + str(err))
        return jsonify({"message": f"Validation error while updating lead {err.messages}", "contact": None}), 406
    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while updating lead\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while updating lead\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"Error: {e}", "contact": None}), 400
    return jsonify({"contact": updated_lead, "message": "Lead is successfully updated"}), 200
    # end update lead block ______________________________


@app.route('/lead/<string:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):

    # auth block ______________________________________________
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received lead delete request")
    # end auth block _____________________________________________

    # delete lead block ____________________________________________
    try:

        deleted_lead = _delete_lead(lead_id)
        logger.info(f"{deleted_lead}")

        delete_lead_status_code = deleted_lead[0]
        delete_lead_message = deleted_lead[1]["id"].get("message")

        if delete_lead_status_code == 422:
            logger.info(f"User was not deleted")
            return jsonify({"message": delete_lead_message, "contact": None}), 422
    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while deleting lead\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while deleting lead\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"Error: {e}", "contact": None}), 400
    logger.info(f"User was deleted")
    return jsonify({"message": delete_lead_message, "contact": True}), 200
    # end delete lead block ______________________________


@app.route('/lead/<string:lead_id>/followers', methods=['POST'])
def add_followers_to_lead(lead_id):

    # auth block ______________________________________________
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received followers request {request.json}")
    # end auth block _____________________________________________

    # delete lead block ____________________________________________
    try:
        validated_data = followers_schema.load(request.json)
        followers = add_followers(lead_id, validated_data)
        logger.info(f"{followers}")
        if followers.get("status_code") == 201:
            logger.info(f"Followers was added")
            return jsonify({"message": f"followers added successfully"}), 201
        elif followers.get("status_code") == 200:
            logger.info(f"Followers was deleted")
            return jsonify({"message": f"followers deleted successfully"}), 200

    except ValidationError as err:
        send_slack_notification("Validation Error while adding followers\n" + str(err))
        logger.error("Validation Error while adding followers\n" + str(err))
        return jsonify({"message": f"Validation error while adding followers {err.messages}"}), 406
    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while adding followers to lead\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while adding followers lead\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"Error: {e}"}), 400
    logger.info(f"followers weren't added")
    return jsonify({"message": f"Something went wrong, followers weren't added"}), 202
    # end delete lead block ______________________________


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
        return jsonify({"message": f"Validation error {err.messages}", "contact": None}), 406
    except Exception as e:
        send_slack_notification("Error while getting lead\n" + str(e))
        logger.error("Error while getting lead\n" + str(e))
        return jsonify({"message": f"Error while getting lead {e}", "contact": None}), 400
    if not lead:
        return jsonify({"message": f"There is no such contact with email = {lead_email}", "contact": None}), 202
    return jsonify({"message": "Successfully get lead by email","contact": lead}), 200


@app.route('/get_lead/<string:lead_id>', methods=['GET'])
def get_lead_by_id(lead_id):
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received get lead by id request. Lead id is {lead_id}")
    try:
        lead = _get_lead_by_id(lead_id)
    except Exception as e:
        send_slack_notification("Error while getting lead by id\n" + str(e))
        logger.error("Error while getting lead by id\n" + str(e))
        return jsonify({"message": f"Error while getting lead by id {e}", "contact": None}), 400
    if lead is False:
        return jsonify({"message": f"There is no such contact with id = {lead_id}", "contact": None}), 202
    return jsonify({"message": "Successfully get lead by id", "contact": lead}), 200


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
        send_slack_notification("Validation Error while getting user\n" + str(err))
        logger.error("Validation Error while getting lead\n" + str(err))
        return jsonify({"message": f"Validation error {err.messages}", "user": None}), 406
    except Exception as e:
        send_slack_notification("Error while getting user\n" + str(e))
        logger.error("Error while getting a user\n" + str(e))
        return jsonify({"message": f"Error while getting a user {e}", "user": None}), 400
    if team_member is False:
        return jsonify({"message": f"There is no such user with email = {lookup_email}", "user": None}), 202
    return jsonify({"message": "Successfully get user by email", "user": team_member}), 200


@app.route('/get_user/<string:lead_id>', methods=['GET'])
def get_user_by_id(lead_id):
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received request to get user by id")
    try:
        team_member = _get_user_by_id(lead_id)
    except Exception as e:
        send_slack_notification("Error while getting user by id\n" + str(e))
        logger.error("Error while getting a user by id\n" + str(e))
        return jsonify({"message": f"Error while getting a user by id{e}", "user": None}), 400
    if team_member is False:
        return jsonify({"message": f"There is no such user with id = {lead_id}", "user": None}), 202
    return jsonify({"message": "Successfully get user by id", "user": team_member}), 200


@app.route('/users', methods=['GET'])
def get_users_list():
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        agents_list = _get_users_list()
    except Exception as e:
        send_slack_notification("Error while getting lead\n" + str(e))
        logger.error("Error while getting a user\n" + str(e))
        return jsonify({"message": f"Error while getting a users list {e}", "users": None}), 400
    if agents_list is False:
        return jsonify({"message": f"There is no users currently in this location", "users": None}), 202
    return jsonify({"message": "Successfully get users list", "users": agents_list}), 200


@app.route('/lead/<string:lead_id>/tags', methods=['PATCH'])
def add_tag_to_lead(lead_id):
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received tags payload:\n{request.json}")

    try:
        validated_data = tags_validation.load(request.json)
        lead = add_tags(ghl_id=lead_id, tags_to_add=validated_data)
        logger.info("Tags added successfully")

    except ValidationError as err:
        send_slack_notification("Validation Error while adding tags\n" + str(err))
        logger.error("Validation Error while adding tags\n" + str(err))
        return jsonify({"message": f"Validation error {err.messages}", "user": None}), 406

    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while adding tags\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while adding tags\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"Error: {e}", "contact": None}), 400

    return jsonify({"message": "Tags added successfully", "contact": lead}), 201


@app.route('/lead/<string:lead_id>/notes', methods=['POST'])
def add_notes_to_lead(lead_id):
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received notes payload:\n{request.json}")

    try:
        validated_data = notes_validation.load(request.json)
        note = create_lead_property_inquiry(ghl_id=lead_id, data=validated_data)
        logger.info("Note added successfully")
        return jsonify({"note": note, "message": "Note added successfully"}), 201

    except ValidationError as err:
        send_slack_notification("Validation Error while adding notes\n" + str(err))
        logger.error("Validation Error while adding notes\n" + str(err))
        return jsonify({"message": f"Validation error {err.messages}", "note": None}), 406

    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while adding tags\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while adding tags\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"error: {e}", "note": None}), 400


@app.route('/lead/<string:lead_id>/tasks', methods=['POST'])
def create_task_endpoint(lead_id):
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    logger.info(f"Received task payload:\n{request.json}")
    try:
        validated_data = task_validation.load(request.json)
        lead_task = create_task(lead_id, validated_data)

    except ValidationError as err:
        send_slack_notification("Validation Error while adding task\n" + str(err))
        logger.error("Validation Error while adding task\n" + str(err))
        return jsonify({"message": f"Validation error {err.messages}", "task": None}), 406

    except Exception as e:
        error_msg = traceback.format_exc()
        send_slack_notification("Error while adding task\n" + str(e) + "\n" + str(error_msg))
        logger.error("Error while adding task\n" + str(e) + "\n" + str(error_msg))
        return jsonify({"message": f"error: {e}", "task": None}), 400

    return jsonify({"task": lead_task, "message": "Task added successfully"}), 200


@app.route('/ponds', methods=['GET'])
def get_ponds_value():
    provided_key = request.headers.get("X-API-KEY")

    if provided_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    logger.info(f"Received request to get ponds")

    ponds = get_ponds()
    if ponds.get("ponds"):
        return jsonify({"message": "Successfully retrieve ponds", "ponds": ponds.get("ponds")}), 200
    return jsonify({"message": "Somthing went wrong", "ponds": None}), 202


if __name__ == '__main__':
    logger.info("Starting app")
    app.run()
