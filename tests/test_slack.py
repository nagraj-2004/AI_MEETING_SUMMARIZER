# from dotenv import load_dotenv
# import os
# from slack_sdk import WebClient

# load_dotenv()

# client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# response = client.chat_postMessage(
#     channel="C09CXKT71H7",  # 👈 replace with your copied channel ID
#     text="Hello from Meeting Summarizer bot!"
# )
# print("✅ Slack message sent:", response["ok"])



from dotenv import load_dotenv
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
channel_id = os.getenv("SLACK_CHANNEL_ID")  # Recommended to use ENV for flexibility

if not (client and channel_id):
    print("⚠️ Slack config missing in .env")
else:
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text="✅ Hello from Meeting Summarizer Bot!"
        )
        if response["ok"]:
            print("✅ Slack message sent successfully")
    except SlackApiError as e:
        print(f"⚠️ Slack API error: {e.response['error']}")
