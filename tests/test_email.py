# from dotenv import load_dotenv
# import os, smtplib

# load_dotenv()

# sender = os.getenv("EMAIL_ADDRESS")
# password = os.getenv("EMAIL_PASSWORD")
# receiver = "your_email@gmail.com"   # test email

# with smtplib.SMTP("smtp.gmail.com", 587) as server:
#     server.starttls()
#     server.login(sender, password)
#     server.sendmail(sender, receiver, "Subject: Test\n\nHello from Python email test!")
#     print("✅ Email sent successfully")


from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText

load_dotenv()

sender = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
receiver = "your_test_email@gmail.com"  # ← Put your personal email to receive test

if not (sender and password):
    print("⚠️ Email config missing in .env")
else:
    try:
        msg = MIMEText("Hello from Python Email Test!", "plain", "utf-8")
        msg["Subject"] = "Test Email"
        msg["From"] = sender
        msg["To"] = receiver

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [receiver], msg.as_string())

        print("✅ Email sent successfully")
    except Exception as e:
        print(f"⚠️ Email send failed: {e}")
