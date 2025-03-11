import os

import requests
import logging

from dotenv import load_dotenv

load_dotenv()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}
UPDATE_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/"


def prepare_lead_data(data: dict) -> dict:
    lead_data = {}
    person_data = data.get("person", {})

    # Helper function to check if a value should be included
    def valid_value(value):
        return value not in (None, "N/A", "", [])

    # Safely extract values with filtering
    email = person_data.get("emails", [{}])[0].get("value")
    phone = person_data.get("phones", [{}])[0].get("value")
    first_name = person_data.get("firstName")
    last_name = person_data.get("lastName")
    assigned_user_id = person_data.get("assignedUserId")

    address = person_data.get("addresses", [{}])[0]
    city = address.get("city")
    state = address.get("state")

    source = data.get("source")
    tags = person_data.get("tags")

    custom_fields = {
        "R3CCQhYeG4kZ5NSTW5vk": person_data.get("customListingType"),
        "F4Bkzj3AXKtBiri6S3Xe": person_data.get("customFB4SRCAURL"),
        "tTqAgy8mKjYaoAWdEqm5": person_data.get("customFB4SLeadID"),
        "t7EBTF8Ub1JgdGl7N5mE": person_data.get("customBuyerProfileFB4S"),
        "5k6Sn4LgOC109kGbPKXA": person_data.get("customFB4SInquiriesCounter"),
        "3kOQc4txrHj7dledzdNJ": person_data.get("customMLSNumber"),
        "EcWFyMMhEZuLm5hz9wpP": person_data.get("customProvince"),
        "fNUZTAUpB0BiA3ff5nSG": person_data.get("customAddress"),
        "yIiyCWtlHAkfKrWwin3H": person_data.get("customCity"),
    }

    # Filter out invalid values
    if valid_value(assigned_user_id):
        lead_data["assignedTo"] = assigned_user_id
    if valid_value(email):
        lead_data["email"] = email
    if valid_value(phone):
        lead_data["phone"] = phone
    if valid_value(first_name):
        lead_data["firstName"] = first_name
    if valid_value(last_name):
        lead_data["lastName"] = last_name
    if valid_value(city):
        lead_data["city"] = city
    if valid_value(state):
        lead_data["state"] = state
    if valid_value(source):
        lead_data["source"] = source
    if valid_value(tags):
        lead_data["tags"] = tags

    filtered_custom_fields = {k: v for k, v in custom_fields.items() if valid_value(v)}
    if filtered_custom_fields:
        lead_data["customField"] = filtered_custom_fields

    return lead_data


def _update_lead(data: dict, ghl_id: str) -> dict:
    prepared_lead_data = prepare_lead_data(data)
    response = requests.put(UPDATE_BASE_URL + ghl_id, headers=HEADERS, json=prepared_lead_data)
    return response.json()
