import os
import requests
import logging

from dotenv import load_dotenv

from utils.create_note import create_lead_property_inquiry

load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}

CREATE_LEAD_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/"
LOOKUP_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/lookup?email="


# Check if such contact already exists in GHL
def ghl_contact_lookup(data, has_property):
    lookup_email = data["person"]["emails"][0].get("value")
    response = requests.get(LOOKUP_BASE_URL + lookup_email, headers=HEADERS)
    logger.info(f"contact look up response\n{response.json()}")

    if response.json().get("contacts"):
        # If contact already exists in GHL and payload contains property - create only note (Property Inquiry)
        if has_property:
            ghl_id = response.json().get("contacts")[0].get("id")
            create_lead_property_inquiry(ghl_id, data)
        return True
    return False


# Preparing json data for ghl api
def prepare_json_data_for_ghl(data: dict) -> dict:
    result = {}
    person_data = data["person"]
    property_data = data.get("property", {})
    result["email"] = person_data["emails"][0].get("value")
    result["phone"] = person_data["phones"][0].get("value")
    result["firstName"] = person_data.get("firstName")
    result["lastName"] = person_data.get("lastName")
    result["city"] = person_data["addresses"][0].get("city")
    result["state"] = person_data["addresses"][0].get("state")
    result["source"] = data.get("source")
    result["tags"] = person_data.get("tags")
    result["customField"] = {
        "R3CCQhYeG4kZ5NSTW5vk": person_data.get("customListingType"),  # Listing Type
        "F4Bkzj3AXKtBiri6S3Xe": person_data.get("customFB4SRCAURL"),  # FB4S RCA URL
        "tTqAgy8mKjYaoAWdEqm5": person_data.get("customFB4SLeadID"),  # FB4S Lead ID
        "t7EBTF8Ub1JgdGl7N5mE": person_data.get("customBuyerProfileFB4S"),  # Buyer Profile FB4S
        "5k6Sn4LgOC109kGbPKXA": person_data.get("customFB4SInquiriesCounter"),  # FB4S Inquiries Counter
        "3kOQc4txrHj7dledzdNJ": person_data.get("customMLSNumber"),  # MLS Number
        "KUpiQ32dAm11q4gu9MB1": person_data.get("customChromeExtensionLink"),  # Chrome Extension Link
        "ULUCaQYI9uurYn8mfpu9": property_data.get("url", "N/A"),  # Listing URL
        "2C3PcAa0JdOHRu95mWzp": person_data.get("customListingURLPath"),  # Listing URL Path
        "pwwHyq93djePQzzMECFI": person_data.get("customAssignedNotFromWillowAt"),  # Assigned Not From Willow At
        "01MYfI09Z919mFibcZNG": person_data.get("customExpectedPriceRange"),  # Expected Price Range
        "EcWFyMMhEZuLm5hz9wpP": person_data.get("customProvince"),  # Province
        "fNUZTAUpB0BiA3ff5nSG": person_data.get("customAddress"),  # Custom Address
        "yIiyCWtlHAkfKrWwin3H": person_data.get("customCity"),  # Custom City
    }
    return result


def create_ghl_lead(data, has_property):
    existing_lead = ghl_contact_lookup(data, has_property)
    if existing_lead:
        return None
    else:
        # if there is no such lead in GHL - create a lead and if payload contains property create note(Property Inquiry)
        prepared_ghl_json = prepare_json_data_for_ghl(data)
        response = requests.post(CREATE_LEAD_BASE_URL, json=prepared_ghl_json, headers=HEADERS)
        if has_property:
            ghl_id = response.json().get("contact").get("id")
            create_lead_property_inquiry(ghl_id, data)
        return response.json()
