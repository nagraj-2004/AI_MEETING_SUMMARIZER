import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SENDER = os.getenv("SMTP_SENDER_EMAIL")
APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")
RECIPIENTS = [e.strip() for e in os.getenv("EMAIL_RECIPIENTS", "").split(",") if e.strip()]

def send_email(subject: str, body: str, recipients: list[str] = None):
    if not (SENDER and APP_PASSWORD):
        print("❌ Email not configured: missing sender or password")
        return  

    recipients = recipients or RECIPIENTS
    if not recipients:
        print("❌ No recipients defined")
        return  

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = ", ".join(recipients)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER, APP_PASSWORD)
            smtp.sendmail(SENDER, recipients, msg.as_string())
        print(f"✅ Email sent to {recipients}")
    except Exception as e:
        print("❌ Email sending error:", e)
