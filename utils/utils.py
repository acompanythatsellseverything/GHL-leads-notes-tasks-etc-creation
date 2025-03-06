import os
import requests
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}

LOOKUP_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/lookup?email="


def _get_lead_by_email(email):
    response = requests.get(LOOKUP_BASE_URL + email, headers=HEADERS)
    if response.json().get("contacts"):
        ghl_id = response.json().get("contacts")[0].get("id")
        logger.info(f"Found lead id by email {email}: {ghl_id}")
        return ghl_id
    logger.info(f"Lead by email {email} was not found")
    return False
