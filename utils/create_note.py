import os

import requests
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}
BASE_NOTES_URL = "https://rest.gohighlevel.com/v1/contacts/"


# Prepare html string for inquiry note
def prepare_inquiry_note(data):
    property = data.get("property")
    url = property.get("url")
    mlsNumber = property.get("mlsNumber")
    description = data.get("description")
    message = data.get("message")
    note = f"""Property Inquiry<br>{url}<br>MLS#{mlsNumber}<br><br>via: FB4S<br><br>{message}<br><br>{description}"""
    return note


def create_lead_property_inquiry(ghl_id: str, data: dict):
    note_body = prepare_inquiry_note(data)
    logger.info(f"Property Inquiry note: {note_body}")
    note_payload = {"body": note_body}
    response = requests.post(BASE_NOTES_URL + ghl_id + "/notes", json=note_payload, headers=HEADERS)
    response = response.json()
    logger.info(f"inquiry response\n{response}")


