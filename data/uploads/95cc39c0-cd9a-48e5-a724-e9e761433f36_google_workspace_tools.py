"""
title: Google Workspace Tools
author: rthidden
author_url: https://hiddendigitalaix.com
git_url: https://github.com/rthidden/google-workspace-tools.git
description: This tool provides comprehensive Google Workspace functionality including Drive, Docs, Sheets, and Slides operations using OAuth 2.0 authentication.
required_open_webui_version: 0.6.18
requirements: google-auth, google-api-python-client, google-auth-httplib2, google-auth-oauthlib, requests
version: 1.0.0
licence: MIT
"""

import json
import os
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel, Field


class Tools:
    def __init__(self):
        """Initialize the Google Workspace Tools."""
        self.valves = self.Valves()
        self.citation = True

    class Valves(BaseModel):
        GOOGLE_CREDENTIALS_FILE: str = Field(
            default="data/opt/oauth_credentials.json",
            description="The path to the Google OAuth client credentials JSON file",
        )
        TOKEN_FILE: str = Field(
            default="data/opt/google_token.json",
            description="The path to store the Google API token",
        )
        SCOPES: List[str] = Field(
            default=[
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/presentations",
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
            ],
            description="Google API scopes required for Google Workspace operations",
        )

    def _get_google_credentials(self):
        """Get Google credentials using OAuth 2.0 flow."""
        creds = None

        # Load existing token
        if os.path.exists(self.valves.TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.valves.TOKEN_FILE, self.valves.SCOPES
                )
                print("Loaded existing credentials")
            except Exception as e:
                print(f"Error loading credentials: {e}")
                # Remove invalid token file
                os.remove(self.valves.TOKEN_FILE)

        # If there are no valid credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("Refreshed expired credentials")
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None

            if not creds:
                # Run the OAuth flow
                if not os.path.exists(self.valves.GOOGLE_CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Google credentials file not found: {self.valves.GOOGLE_CREDENTIALS_FILE}"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.valves.GOOGLE_CREDENTIALS_FILE, self.valves.SCOPES
                )
                # This will open a browser window for authentication
                creds = flow.run_local_server(port=0)
                print("Completed OAuth flow")

            # Save the credentials for the next run
            with open(self.valves.TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
                print(f"Saved credentials to {self.valves.TOKEN_FILE}")

        return creds

    def authenticate_google_workspace(self) -> str:
        """
        Authenticate with Google Workspace services. This will open a browser window for OAuth authorization.
        Call this function first before using any other Google Workspace tools.

        :return: Status message indicating success or failure of authentication.
        """
        try:
            creds = self._get_google_credentials()
            if creds and creds.valid:
                return "✅ Successfully authenticated with Google Workspace! You can now use all Google Workspace tools."
            else:
                return "❌ Authentication failed. Please check your credentials file and try again."
        except Exception as e:
            print(f"Authentication error: {e}")
            return f"❌ Authentication error: {str(e)}"

    def list_google_drive_files(
        self, max_results: int = 10, folder_id: Optional[str] = None
    ) -> str:
        """
        List files in Google Drive.

        :param max_results: Maximum number of files to return (default: 10).
        :param folder_id: ID of a specific folder to list files from (optional).
        :return: JSON string containing the list of files.
        """
        try:
            creds = self._get_google_credentials()
            service = build("drive", "v3", credentials=creds)

            query = ""
            if folder_id:
                query = f"'{folder_id}' in parents"

            results = (
                service.files()
                .list(
                    pageSize=max_results,
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink)",
                )
                .execute()
            )

            items = results.get("files", [])

            if not items:
                return "No files found."

            files_data = []
            for item in items:
                files_data.append(
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "mimeType": item.get("mimeType", "Unknown"),
                        "modifiedTime": item.get("modifiedTime", "Unknown"),
                        "size": item.get("size", "Unknown"),
                        "webViewLink": item.get("webViewLink", "No link"),
                    }
                )

            return json.dumps(files_data, indent=2)

        except Exception as e:
            print(f"Error listing Drive files: {e}")
            return f"Error listing Drive files: {str(e)}"

    def create_google_doc(self, title: str, content: str = "") -> str:
        """
        Create a new Google Document.

        :param title: The title of the document.
        :param content: Initial content for the document (optional).
        :return: Document ID and view link.
        """
        try:
            creds = self._get_google_credentials()

            # Create the document
            docs_service = build("docs", "v1", credentials=creds)
            doc = docs_service.documents().create(body={"title": title}).execute()
            doc_id = doc["documentId"]

            # Add content if provided
            if content:
                requests_body = [
                    {"insertText": {"location": {"index": 1}, "text": content}}
                ]

                docs_service.documents().batchUpdate(
                    documentId=doc_id, body={"requests": requests_body}
                ).execute()

            # Get the document link
            drive_service = build("drive", "v3", credentials=creds)
            file = (
                drive_service.files().get(fileId=doc_id, fields="webViewLink").execute()
            )

            result = {
                "documentId": doc_id,
                "title": title,
                "webViewLink": file["webViewLink"],
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            print(f"Error creating Google Doc: {e}")
            return f"Error creating Google Doc: {str(e)}"

    def create_google_sheet(
        self, title: str, data: Optional[List[List[str]]] = None
    ) -> str:
        """
        Create a new Google Spreadsheet.

        :param title: The title of the spreadsheet.
        :param data: Initial data for the spreadsheet as a list of rows (optional).
        :return: Spreadsheet ID and view link.
        """
        try:
            creds = self._get_google_credentials()
            sheets_service = build("sheets", "v4", credentials=creds)

            # Create the spreadsheet
            spreadsheet = {"properties": {"title": title}}

            result = sheets_service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result["spreadsheetId"]

            # Add data if provided
            if data:
                body = {"values": data}
                sheets_service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range="A1",
                    valueInputOption="RAW",
                    body=body,
                ).execute()

            # Get the spreadsheet link
            drive_service = build("drive", "v3", credentials=creds)
            file = (
                drive_service.files()
                .get(fileId=spreadsheet_id, fields="webViewLink")
                .execute()
            )

            result = {
                "spreadsheetId": spreadsheet_id,
                "title": title,
                "webViewLink": file["webViewLink"],
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            print(f"Error creating Google Sheet: {e}")
            return f"Error creating Google Sheet: {str(e)}"

    def read_google_sheet_data(
        self, spreadsheet_id: str, range_name: str = "A1:Z100"
    ) -> str:
        """
        Read data from a Google Spreadsheet.

        :param spreadsheet_id: The ID of the spreadsheet.
        :param range_name: The range to read (e.g., 'A1:Z100').
        :return: JSON string containing the spreadsheet data.
        """
        try:
            creds = self._get_google_credentials()
            sheets_service = build("sheets", "v4", credentials=creds)

            result = (
                sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])

            if not values:
                return "No data found in the specified range."

            return json.dumps(values, indent=2)

        except Exception as e:
            print(f"Error reading Google Sheet: {e}")
            return f"Error reading Google Sheet: {str(e)}"

    def search_google_drive(self, query: str, max_results: int = 10) -> str:
        """
        Search for files in Google Drive.

        :param query: Search query (file name, content, etc.).
        :param max_results: Maximum number of results to return.
        :return: JSON string containing search results.
        """
        try:
            creds = self._get_google_credentials()
            service = build("drive", "v3", credentials=creds)

            # Search for files
            results = (
                service.files()
                .list(
                    q=f"name contains '{query}' or fullText contains '{query}'",
                    pageSize=max_results,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
                )
                .execute()
            )

            items = results.get("files", [])

            if not items:
                return f"No files found matching '{query}'."

            files_data = []
            for item in items:
                files_data.append(
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "mimeType": item.get("mimeType", "Unknown"),
                        "modifiedTime": item.get("modifiedTime", "Unknown"),
                        "webViewLink": item.get("webViewLink", "No link"),
                    }
                )

            return json.dumps(files_data, indent=2)

        except Exception as e:
            print(f"Error searching Google Drive: {e}")
            return f"Error searching Google Drive: {str(e)}"

    def get_google_doc_content(self, document_id: str) -> str:
        """
        Get the content of a Google Document.

        :param document_id: The ID of the document.
        :return: The text content of the document.
        """
        try:
            creds = self._get_google_credentials()
            docs_service = build("docs", "v1", credentials=creds)

            doc = docs_service.documents().get(documentId=document_id).execute()
            content = doc.get("body", {}).get("content", [])

            text_content = ""
            for element in content:
                if "paragraph" in element:
                    for text_element in element["paragraph"].get("elements", []):
                        if "textRun" in text_element:
                            text_content += text_element["textRun"].get("content", "")

            return (
                text_content
                if text_content.strip()
                else "Document appears to be empty."
            )

        except Exception as e:
            print(f"Error getting Google Doc content: {e}")
            return f"Error getting Google Doc content: {str(e)}"
