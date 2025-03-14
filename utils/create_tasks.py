import os

import requests
import logging

from dotenv import load_dotenv

from utils.utils import _get_lead_by_id

load_dotenv()

logger = logging.getLogger()

GHL_API_KEY = os.getenv('GHL_API_KEY')
HEADERS = {'Authorization': f'Bearer {GHL_API_KEY}'}
BASE_TASK_URL = "https://rest.gohighlevel.com/v1/contacts/"


# Prepare html string for inquiry note
def prepare_task_payload(data, lead):
    task = {}
    task["title"] = data.get("title")
    task["dueDate"] = data.get("dueDate")
    task["description"] = data.get("description")
    task["assignedTo"] = lead.get("assignedTo")
    task["status"] = "incompleted"
    return task


def create_task(ghl_id: str, data: dict):
    lead = _get_lead_by_id(ghl_id)
    task_body = prepare_task_payload(data, lead)
    response = requests.post(BASE_TASK_URL + ghl_id + "/tasks", json=task_body, headers=HEADERS)
    response = response.json()
    logger.info(f"Create task response\n{response}")
    return response


