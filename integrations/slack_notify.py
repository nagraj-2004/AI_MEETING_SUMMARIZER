import json
import os
import requests

WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

def send_slack_message(text: str) -> None:
    """Send a message via Incoming Webhook (simplest) or chat.postMessage if configured."""
    if WEBHOOK:
        payload = {"text": text}
        requests.post(WEBHOOK, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        return

    if BOT_TOKEN and CHANNEL_ID:
        url = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": f"Bearer {BOT_TOKEN}", "Content-Type": "application/json; charset=utf-8"}
        data = {"channel": CHANNEL_ID, "text": text}
        requests.post(url, headers=headers, data=json.dumps(data))
