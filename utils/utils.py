import os
import requests
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}

LOOKUP_LEAD_URL = "https://rest.gohighlevel.com/v1/contacts/lookup?email="
BASIC_USER_URL = "https://rest.gohighlevel.com/v1/users/"
CONTACT_URL = "https://rest.gohighlevel.com/v1/contacts/"
MAKE_GHL_2_0_AUTH_URL = os.getenv('MAKE_GHL_2_0_AUTH_URL')


def _get_lead_by_id(ghl_id):
    payload = {"id": ghl_id, "action": "get_by_id"}
    response = requests.get(MAKE_GHL_2_0_AUTH_URL, json=payload, headers=HEADERS)
    if response.json().get("contact"):
        contact = response.json().get("contact")
        logger.info(f"Found lead by id: {contact}")
        return contact
    return False


def _get_lead_by_email(email):
    payload = {"email": email, "action": "get_by_email"}
    response = requests.post(MAKE_GHL_2_0_AUTH_URL, json=payload, headers=HEADERS)
    if response.json().get("contacts"):
        contact = response.json().get("contacts")[0]
        logger.info(f"Found lead id by email {email}: {contact}")
        return contact
    logger.info(f"Lead by email {email} was not found")
    return False


def _get_user_by_email(email):
    response = requests.get(BASIC_USER_URL, headers=HEADERS)
    if response.json().get("users"):
        for user in response.json().get("users"):
            if user.get("email") == email:
                logger.info(f"Found user by email {email}: {user}")
                return user
    logger.info(f"User with email:{email} was not found")
    return False


def _get_user_by_id(ghl_id):
    response = requests.get(BASIC_USER_URL + ghl_id, headers=HEADERS)
    return response.json()


def _get_users_list():
    response = requests.get(BASIC_USER_URL, headers=HEADERS)
    if response.json().get("users"):
        return response.json().get("users")
    return False
