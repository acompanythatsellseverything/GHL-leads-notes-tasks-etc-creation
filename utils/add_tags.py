import os
import requests
import logging

from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}

LEAD_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/"


def get_existing_tags(ghl_id):
    response = requests.get(f'{LEAD_BASE_URL}{ghl_id}', headers=HEADERS)
    return response.json()["contact"].get('tags', [])


def add_tags(ghl_id: str, tags_to_add: list):
    # Getting existing tags and combine it with new tags
    tags = get_existing_tags(ghl_id)
    tags.extend(tags_to_add.get("tags"))
    payload = {"tags": tags}
    response = requests.put(LEAD_BASE_URL + ghl_id, headers=HEADERS, json=payload)
    return response.json()
