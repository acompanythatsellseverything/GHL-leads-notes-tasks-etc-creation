import os

import requests
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}
LOOKUP_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/lookup?email="
UPDATE_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/"


def prepare_lead_data(data: dict) -> dict:
    lead_data = {}
    person_data = data["person"]
    lead_data["email"] = person_data["emails"][0].get("value")
    lead_data["phone"] = person_data["phones"][0].get("value")
    lead_data["firstName"] = person_data.get("firstName")
    lead_data["lastName"] = person_data.get("lastName")
    lead_data["city"] = person_data["addresses"][0].get("city")
    lead_data["state"] = person_data["addresses"][0].get("state")
    lead_data["source"] = data.get("source")
    lead_data["tags"] = person_data.get("tags")
    lead_data["customField"] = {
        "R3CCQhYeG4kZ5NSTW5vk": person_data.get("customListingType"),  # Listing Type
        "F4Bkzj3AXKtBiri6S3Xe": person_data.get("customFB4SRCAURL"),  # FB4S RCA URL
        "tTqAgy8mKjYaoAWdEqm5": person_data.get("customFB4SLeadID"),  # FB4S Lead ID
        "t7EBTF8Ub1JgdGl7N5mE": person_data.get("customBuyerProfileFB4S"),  # Buyer Profile FB4S
        "5k6Sn4LgOC109kGbPKXA": person_data.get("customFB4SInquiriesCounter"),  # FB4S Inquiries Counter
        "3kOQc4txrHj7dledzdNJ": person_data.get("customMLSNumber"),  # MLS Number
        "EcWFyMMhEZuLm5hz9wpP": person_data.get("customProvince"),  # Province
        "fNUZTAUpB0BiA3ff5nSG": person_data.get("customAddress"),  # Custom Address
        "yIiyCWtlHAkfKrWwin3H": person_data.get("customCity"),  # Custom City
    }
    return lead_data


def ghl_contact_lookup(data: dict):
    lookup_email = data["person"]["emails"][0].get("value")
    response = requests.get(LOOKUP_BASE_URL + lookup_email, headers=HEADERS)
    logger.info(f"contact look up response\n{response.json()}")
    if response.json().get("contacts"):
        ghl_id = response.json().get("contacts")[0].get("id")
        return ghl_id
    return False


def update_lead(data: dict) -> dict:
    ghl_id = ghl_contact_lookup(data)
    if ghl_id is False:
        return {"error": "Contact not found"}
    prepared_lead_data = prepare_lead_data(data)
    response = requests.put(UPDATE_BASE_URL + ghl_id, headers=HEADERS, json=prepared_lead_data)
    return response.json()
