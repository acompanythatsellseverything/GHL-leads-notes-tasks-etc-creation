import os
import requests

from dotenv import load_dotenv

load_dotenv()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}

CREATE_LEAD_BASE_URL = "https://rest.gohighlevel.com/v1/contacts/"

def create_ghl_lead(data):
    response = requests.post(CREATE_LEAD_BASE_URL, json=data, headers=HEADERS)
    if response.json()['contact'].get("id"):
        return response.json()
    else:
        return {"User was not created": response.json()}
