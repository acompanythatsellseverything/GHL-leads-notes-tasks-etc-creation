import os
import requests
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}

DELETE_LEAD_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/"

def _delete_lead(lead_id):
    response = requests.delete(DELETE_LEAD_BASE_URL + lead_id, headers=HEADERS)
    if response.status_code == 200:
        return 200, {"id":{"message":"Successfully deleted"}}
    elif response.status_code == 422:
        return 422, response.json()