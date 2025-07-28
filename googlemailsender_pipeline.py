"""
title: GoogleMailSender Pipeline
author: lamachine.geo
date: 2024-03-19
version: 1.0
license: MIT
description: A pipeline for managing Gmail using Google's API.
requirements: google-auth-oauthlib, google-auth-httplib2, google-api-python-client
"""

"""
Index out of range error on upload
"""

import base64
import json
import os
import pickle
from email.mime.text import MIMEText
from typing import List

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        GOOGLE_CLIENT_SECRET_FILE: str = Field(
            default="client_secret.json",
            description="The path to the Google client secret file",
        )
        TOKEN_PATH: str = Field(
            default="token.pickle",
            description="The path to store the Google API token",
        )
        SCOPES: List[str] = Field(
            default=[
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://mail.google.com/",
            ],
            description="Google API scopes required for Gmail operations",
        )

    def __init__(self):
        self.valves = self.Valves()
        self._service = None

    def _get_gmail_service(self):
        """Initialize and return the Gmail service."""
        if not self._service:
            creds = None
            if os.path.exists(self.valves.TOKEN_PATH):
                with open(self.valves.TOKEN_PATH, "rb") as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.valves.GOOGLE_CLIENT_SECRET_FILE, self.valves.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                with open(self.valves.TOKEN_PATH, "wb") as token:
                    pickle.dump(creds, token)

            self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """
        print(__user__)
        result = ""

        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"

        if result == "":
            result = "User: Unknown"

        return result

    def send_email(self, subject: str, body: str, recipients: List[str]) -> str:
        """
        Send an email using Gmail API. Sign it with the user's name and indicate that it is an AI generated email.
        DO NOT SEND WITHOUT USER'S CONSENT. CONFIRM CONSENT AFTER SHOWING USER WHAT YOU PLAN TO SEND.

        :param subject: The subject of the email.
        :param body: The body of the email.
        :param recipients: The list of recipient email addresses.
        :return: The result of the email sending operation.
        """
        try:
            service = self._get_gmail_service()
            message = MIMEText(body)
            message["to"] = ", ".join(recipients)
            message["subject"] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            result = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw})
                .execute()
            )

            return f"Message sent:\n   TO: {str(recipients)}\n   SUBJECT: {subject}\n   BODY: {body}"
        except Exception as e:
            return str({"status": "error", "message": f"{str(e)}"})

    def list_emails(self, max_results: int = 10) -> str:
        """
        List recent emails from Gmail inbox.

        :param max_results: Maximum number of emails to return.
        :return: JSON string containing email list.
        """
        try:
            service = self._get_gmail_service()
            results = (
                service.users()
                .messages()
                .list(userId="me", maxResults=max_results, labelIds=["INBOX"])
                .execute()
            )

            messages = []
            for msg in results.get("messages", []):
                message = (
                    service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="metadata")
                    .execute()
                )
                headers = message["payload"]["headers"]
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No Subject",
                )
                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"), "Unknown"
                )
                messages.append({"id": msg["id"], "subject": subject, "from": sender})

            return json.dumps(messages, indent=2)
        except Exception as e:
            return str({"status": "error", "message": f"{str(e)}"})

    def delete_email(self, message_id: str) -> str:
        """
        Delete a specific email.

        :param message_id: ID of the email to delete.
        :return: Result of the deletion operation.
        """
        try:
            service = self._get_gmail_service()
            service.users().messages().delete(userId="me", id=message_id).execute()
            return str(
                {
                    "status": "success",
                    "message": f"Email {message_id} deleted successfully",
                }
            )
        except Exception as e:
            return str({"status": "error", "message": f"{str(e)}"})
