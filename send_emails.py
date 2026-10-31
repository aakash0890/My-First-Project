import os
import base64
import csv
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def gmail_service():
    creds = None

    # Use existing authorization
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # Re-authorize only if necessary
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_email(service, receiver, subject, message):

    email = MIMEText(message)

    email["to"] = receiver
    email["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        email.as_bytes()
    ).decode()

    body = {
        "raw": encoded_message
    }

    service.users().messages().send(
        userId="me",
        body=body
    ).execute()

    print(f"Email sent to: {receiver}")


# Connect to Gmail
service = gmail_service()


# Read contacts.csv
with open("email_template.txt", "r", encoding="utf-8") as template_file:
    template = template_file.read()


with open("contacts.csv", "r", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for contact in reader:

        name = contact["name"]
        email = contact["email"]
        

        subject = f"Registration Confirmation "

        message = template.replace("{{name}}", name)
        

        send_email(
            service,
            email,
            subject,
            message
        )

        


