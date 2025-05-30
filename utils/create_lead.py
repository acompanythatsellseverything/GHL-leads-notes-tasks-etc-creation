import os
import requests
import logging

from dotenv import load_dotenv

from utils.create_note import create_lead_property_inquiry
from utils.utils import _get_user_by_email

load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv("GHL_API_KEY")
HEADERS = {"Authorization": f"Bearer {GHL_API_KEY}"}

CREATE_LEAD_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/"
LOOKUP_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/lookup?email="
AUTO_ASSIGN_URL = os.getenv("AUTO_ASSIGN_URL")


BACKUP_ASSIGN_USER = {
    "firstName": "Willow",
    "id": "9pXq0rOQJOUWOxDmnMHP",
    "lastName": "Sweet",
    "name": "Willow Sweet",
}


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


def prepare_json_data_for_auto_assign(data: dict) -> dict:
    result = {}
    property_data = data.get("property")
    result["listing_mls"] = property_data["mlsNumber"]
    result["listing_zip"] = property_data["code"]
    result["listing_city"] = property_data["city"]
    result["listing_province"] = property_data["state"]
    result["buyer_email"] = data["person"]["emails"][0].get("value")
    result["buyer_city"] = data["person"].get("CustomCity")
    result["buyer_province"] = data["person"].get("CustomProvince")
    result["cold_lead"] = 0
    result["buyer_name"] = (
        data["person"].get("firstName") + " " + data["person"].get("lastName")
    )
    return result


# Preparing json data for ghl api
def prepare_json_data_for_ghl(data: dict) -> dict:
    result = {}
    person_data = data["person"]
    assigned_realtor = person_data.get("selected_realtor_email")
    auto_assigned_realtor = person_data.get("auto_assign_user_id")
    if assigned_realtor: # If original payload have selected_realtor_email then it's manual assign
        team_member = _get_user_by_email(assigned_realtor)
        result["assignedTo"] = team_member.get("id")
    if auto_assigned_realtor: # If original payload doesn't have selected_realtor_email then it's auto assign
        result["assignedTo"] = auto_assigned_realtor
    else: # If there is no selected_realtor_email and no property then lead is assigned to willow master acc
        logger.info("No suitable users were found to auto-assign. Assign to Willow-master acc")
        result["assignedTo"] = BACKUP_ASSIGN_USER.get("id")
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
        "WfBlGcyHtMZIy885bv2q": person_data.get("customStage"), # Stage
        "zkkxcKSBxGG0AwKg7zb9": person_data.get("customPrice"), # Price
        "kN2l6aNW601zksRV5L0D": person_data.get("customClosingAnniversary"), # Closing Anniversary
        "xNiTcYOSPKyG6UK9PHEn": person_data.get("customYlopoSellerReport"), # Ylopo Seller Report
        "uvG7VhHmPyqjD976RNoW": person_data.get("customParentCategory"), # Parent Category
        "fkIooCxVyocAQeMlwWAo": person_data.get("customWhoareyou"), # Who are you?
        "BWFdoHapnpo04EHpG5F0": person_data.get("customLastActivity"), # Last Activity
        "SBQ7tdjkwFMumNkfGrHw": person_data.get("customCloseDate"), # Close Date
        "SujDeGnOKJXlifbU7fLo": person_data.get("customLisitngPushesSent"), # Lisitng Pushes Sent
        "gpGUaXRBHdURtrh7nmlF": person_data.get("customYlopoStarsLink"), # Ylopo Stars Link
        "LzbUJkxo7kRClIomCc0U": person_data.get("customOldID"), # Old ID
    }
    return result


def get_user_to_auto_assign(data: dict):
    users = requests.get( # In production change port from 5000 to 5007
        "http://127.0.0.1:5007/users", headers={"x-api-key": os.getenv("FLASK_API_KEY")}
    ).json()

    potential_number_1_user = data.get("assigned_realtor")
    possible_users = data.get("possible_realtors")
    for user in users["users"]: # Find potential user GHL id
        if user.get("email") == potential_number_1_user:
            return user
    for possible_user in possible_users: # If potential user were not found in GHL user - we search by possible users
        for user in users["users"]:
            if user.get("email") == possible_user:
                return user
    # If we don't find realtor to assign - we assign lead to willow-master acc
    return BACKUP_ASSIGN_USER


def create_ghl_lead(data, has_property):
    existing_lead = ghl_contact_lookup(data, has_property)
    if existing_lead:
        return None
    else:
        # if there is no such lead in GHL - create a lead and if payload contains property create note(Property Inquiry)
        if has_property and not data.get("selected_realtor_email"):
            assign_payload = prepare_json_data_for_auto_assign(data)
            auto_assign_response = requests.post(AUTO_ASSIGN_URL, json=assign_payload)
            existing_possible_realtor = get_user_to_auto_assign(auto_assign_response.json())
            logger.info(f"Realtor to auto assign: {existing_possible_realtor}")
            data["person"]["auto_assign_user_id"] = existing_possible_realtor.get("id")

        prepared_ghl_json = prepare_json_data_for_ghl(data)
        logger.info(f"{prepared_ghl_json}")
        response = requests.post(
            CREATE_LEAD_BASE_URL, json=prepared_ghl_json, headers=HEADERS
        )
        if has_property:
            ghl_id = response.json().get("contact").get("id")
            create_lead_property_inquiry(ghl_id, data)
        return response.json()
