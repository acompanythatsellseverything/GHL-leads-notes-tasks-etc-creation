import logging
import os

import requests

from dotenv import load_dotenv

from utils.utils import _get_user_by_email

logger = logging.getLogger()

load_dotenv()

GHL_API_KEY = os.getenv('GHL_API_KEY')
MAKE_2_0_AUTH_URL = os.getenv('MAKE_GHL_2_0_AUTH_URL')
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
    assigned_user_email = person_data.get("selected_realtor_email")

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
        "WfBlGcyHtMZIy885bv2q": person_data.get("customStage"),
        "qe4zFdjyWpWlKjUkJ1Oz": person_data.get("pond"),
        "zkkxcKSBxGG0AwKg7zb9": person_data.get("customPrice"),
        "kN2l6aNW601zksRV5L0D": person_data.get("customClosingAnniversary"),
        "KUpiQ32dAm11q4gu9MB1": person_data.get("customChromeExtensionLink"),
        "2C3PcAa0JdOHRu95mWzp": person_data.get("customListingURLPath"),
        "xNiTcYOSPKyG6UK9PHEn": person_data.get("customYlopoSellerReport"),
        "fkIooCxVyocAQeMlwWAo": person_data.get("customWhoareyou"),
        "uvG7VhHmPyqjD976RNoW": person_data.get("customParentCategory"),
        "BWFdoHapnpo04EHpG5F0": person_data.get("customLastActivity"),
        "SBQ7tdjkwFMumNkfGrHw": person_data.get("customCloseDate"),
        "SujDeGnOKJXlifbU7fLo": person_data.get("customLisitngPushesSent"),
        "gpGUaXRBHdURtrh7nmlF": person_data.get("customYlopoStarsLink"),
        "pwwHyq93djePQzzMECFI": person_data.get("customAssignedNotFromWillowAt"),
        "01MYfI09Z919mFibcZNG": person_data.get("customExpectedPriceRange"),
        "Cv7kNq7m8CBVDh7n9XEj": person_data.get("customAbandonedPondReason"),
        "LzbUJkxo7kRClIomCc0U": person_data.get("customOldID")
    }

    # Filter out invalid values
    if valid_value(assigned_user_email):
        lead_data["assignedTo"] = _get_user_by_email(assigned_user_email).get("id")
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


def _update_lead(data: dict, ghl_id: str):
    prepared_lead_data = prepare_lead_data(data)
    response = requests.put(UPDATE_BASE_URL + ghl_id, headers=HEADERS, json=prepared_lead_data)
    logger.info(f"Prepared update data {prepared_lead_data}")
    contact = response.json().get("contact")
    if contact:
        return contact
    return False


def add_followers(lead_id: str, data: dict):
    data["url"] = f"/contacts/{lead_id}/followers"
    raw_followers = data["followers"]
    print(raw_followers)
    data["body"] = str({"followers": raw_followers})
    print(data)
    response = requests.post(MAKE_2_0_AUTH_URL, json=data)
    return response.json()
