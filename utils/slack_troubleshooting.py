import os

import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

Slack_URL = f"https://hooks.slack.com/services/{SLACK_WEBHOOK_URL}"


def send_slack_notification(message: str):
    requests.post(Slack_URL, json={"text": message})

