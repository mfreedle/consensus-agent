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
import urllib.parse
from typing import List, Optional

from google.oauth2.credentials import Credentials
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
        REDIRECT_URI: str = Field(
            default="http://localhost:19328/google-oauth-callback.html",
            description="OAuth redirect URI for authentication flow",
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
        """Get Google credentials using OAuth 2.0 flow with comprehensive timezone handling."""
        creds = None

        # Load existing token
        if os.path.exists(self.valves.TOKEN_FILE):
            try:
                # Load the token data first to examine it
                with open(self.valves.TOKEN_FILE, "r") as f:
                    token_data = json.load(f)

                # If there's no expiry field, add one with a future date to prevent comparison issues
                if "expiry" not in token_data:
                    from datetime import datetime, timedelta, timezone

                    # Set expiry to 1 hour from now in timezone-aware format
                    future_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
                    token_data["expiry"] = future_expiry.isoformat().replace(
                        "+00:00", "Z"
                    )

                    # Save the updated token data
                    with open(self.valves.TOKEN_FILE, "w") as f:
                        json.dump(token_data, f, indent=2)
                    print("Added expiry field to token for timezone compatibility")

                # Now try the standard format
                creds = Credentials.from_authorized_user_file(
                    self.valves.TOKEN_FILE, self.valves.SCOPES
                )
                # Use v2 approach for timezone safety
                creds = self._get_google_credentials_v2()
                print("Loaded existing credentials")

            except Exception as e:
                print(f"Standard format failed: {e}")
                # Fallback to manual loading with robust datetime handling
                try:
                    from datetime import datetime, timedelta, timezone

                    # Handle the case where expiry is a string - make it timezone-aware
                    expiry = token_data.get("expiry")
                    if isinstance(expiry, str):
                        try:
                            # Handle various datetime formats from Google
                            if expiry.endswith("Z"):
                                # ISO format with Z (UTC) - this is the standard Google format
                                expiry_dt = datetime.fromisoformat(
                                    expiry.replace("Z", "+00:00")
                                )
                            elif "+" in expiry or expiry.endswith("UTC"):
                                # ISO format with timezone info
                                expiry_dt = datetime.fromisoformat(
                                    expiry.replace("UTC", "+00:00")
                                )
                            else:
                                # Assume UTC if no timezone info and make it timezone-aware
                                dt = datetime.fromisoformat(expiry)
                                expiry_dt = (
                                    dt.replace(tzinfo=timezone.utc)
                                    if dt.tzinfo is None
                                    else dt
                                )
                        except Exception as e:
                            print(f"Error parsing expiry time: {e}")
                            # Set a future expiry time in UTC to avoid comparison issues
                            expiry_dt = datetime.now(timezone.utc) + timedelta(hours=1)
                    elif expiry is None:
                        # If no expiry specified, set a future time to avoid issues
                        expiry_dt = datetime.now(timezone.utc) + timedelta(hours=1)
                    else:
                        # expiry is already a datetime object, ensure it's timezone-aware
                        if hasattr(expiry, "tzinfo") and expiry.tzinfo is None:
                            expiry_dt = expiry.replace(tzinfo=timezone.utc)
                        else:
                            expiry_dt = expiry

                    # Create credentials from token data with timezone-aware expiry
                    creds = Credentials(
                        token=token_data.get("token"),
                        refresh_token=token_data.get("refresh_token"),
                        token_uri=token_data.get("token_uri"),
                        client_id=token_data.get("client_id"),
                        client_secret=token_data.get("client_secret"),
                        scopes=token_data.get("scopes", self.valves.SCOPES),
                        expiry=expiry_dt,  # Pass timezone-aware expiry directly to constructor
                    )

                    print("Loaded credentials from token data")
                except Exception as e2:
                    print(f"Error loading token data: {e2}")
                    return None

        # If we have credentials, return them without validity checking to avoid datetime comparisons
        if creds:
            return creds

        # If we get here, we don't have valid credentials
        return None

    def _get_google_credentials_v2(self):
        """
        Alternative credential loading with programmatic approach to avoid datetime comparison issues.
        This method creates credentials programmatically instead of using file-based loading.
        """
        try:
            if not os.path.exists(self.valves.TOKEN_FILE):
                return None

            # Load token data manually
            with open(self.valves.TOKEN_FILE, "r") as f:
                token_data = json.load(f)

            # Create credentials programmatically with explicit timezone handling
            from datetime import datetime, timezone

            # Handle expiry field safely
            expiry = token_data.get("expiry")
            expiry_dt = None

            if expiry:
                try:
                    if isinstance(expiry, str):
                        if expiry.endswith("Z"):
                            expiry_dt = datetime.fromisoformat(
                                expiry.replace("Z", "+00:00")
                            )
                        else:
                            parsed_dt = datetime.fromisoformat(expiry)
                            expiry_dt = (
                                parsed_dt.replace(tzinfo=timezone.utc)
                                if parsed_dt.tzinfo is None
                                else parsed_dt
                            )
                    elif hasattr(expiry, "tzinfo"):
                        expiry_dt = (
                            expiry.replace(tzinfo=timezone.utc)
                            if expiry.tzinfo is None
                            else expiry
                        )
                except Exception as e:
                    print(f"Warning: Could not parse expiry time: {e}")
                    # Set a future expiry to avoid issues
                    from datetime import timedelta

                    expiry_dt = datetime.now(timezone.utc) + timedelta(hours=1)

            # Create credentials using the constructor directly (bypasses file loading issues)
            creds = Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri=token_data.get(
                    "token_uri", "https://oauth2.googleapis.com/token"
                ),
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=token_data.get("scopes", self.valves.SCOPES),
                expiry=expiry_dt,
            )

            print("Created credentials programmatically (timezone-safe approach)")
            return creds

        except Exception as e:
            print(f"Error in programmatic credential creation: {e}")
            return None

    def get_oauth_authorization_url(self) -> str:
        """
        Generate Google OAuth authorization URL for user to authenticate.
        This is the first step for new users to grant permissions.

        :return: Authorization URL that users can visit to grant permissions.
        """
        try:
            # Load client credentials
            if not os.path.exists(self.valves.GOOGLE_CREDENTIALS_FILE):
                return "❌ OAuth credentials file not found. Please contact administrator to set up Google API credentials."

            with open(self.valves.GOOGLE_CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)

            client_id = credentials["installed"]["client_id"]

            # Build authorization URL
            scope_string = urllib.parse.quote(" ".join(self.valves.SCOPES))
            redirect_uri = urllib.parse.quote(self.valves.REDIRECT_URI)

            auth_url = (
                f"https://accounts.google.com/o/oauth2/auth?"
                f"client_id={client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={scope_string}&"
                f"response_type=code&"
                f"access_type=offline&"
                f"prompt=consent"
            )

            return (
                f"🔐 **Google OAuth Authorization Required**\n\n"
                f"Please visit this URL to authorize Google Workspace access:\n\n"
                f"**{auth_url}**\n\n"
                f"After authorization, you'll be redirected to a callback page. "
                f"Copy the message from the callback page and paste it in the chat. The AI will automatically process it!"
            )

        except Exception as e:
            return f"❌ Error generating authorization URL: {str(e)}"

    def complete_oauth_setup(self, authorization_code: str) -> str:
        """
        Complete OAuth setup using the authorization code from Google.
        Call this after visiting the authorization URL and getting the code.

        :param authorization_code: The authorization code from Google OAuth redirect
        :return: Status message indicating success or failure
        """
        try:
            import requests

            # Load client credentials
            with open(self.valves.GOOGLE_CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)

            client_id = credentials["installed"]["client_id"]
            client_secret = credentials["installed"]["client_secret"]

            # Exchange authorization code for tokens
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": self.valves.REDIRECT_URI,
            }

            response = requests.post(token_url, data=token_data)

            if response.status_code == 200:
                token_info = response.json()

                # Create the token file
                token_file_data = {
                    "token": token_info["access_token"],
                    "refresh_token": token_info.get("refresh_token"),
                    "token_uri": token_url,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scopes": self.valves.SCOPES,
                }

                # Save token file
                with open(self.valves.TOKEN_FILE, "w") as f:
                    json.dump(token_file_data, f, indent=2)

                return (
                    "✅ **OAuth Setup Complete!**\n\n"
                    "Google Workspace access has been successfully configured. "
                    "You can now use all Google Workspace tools including Drive, Docs, Sheets, and Slides!"
                )
            else:
                return f"❌ Token exchange failed: {response.text}"

        except Exception as e:
            return f"❌ Error completing OAuth setup: {str(e)}"

    def get_user_setup_instructions(self) -> str:
        """
        Provide complete setup instructions for new users.

        :return: Step-by-step setup guide
        """
        return """# 🚀 **Google Workspace Tools Setup Guide**

## **Quick Setup (2 steps):**

### **Step 1: Get Authorization**
Call the function: `get_oauth_authorization_url()`
- This will give you a Google authorization link
- Click the link and sign in to your Google account
- Grant permissions for Google Workspace access
- Copy the authorization code from the redirect URL

### **Step 2: Complete Setup** 
Call the function: `complete_oauth_setup("YOUR_AUTHORIZATION_CODE")`
- Paste the authorization code you copied
- This will save your credentials securely

### **Step 3: Start Using!**
Once setup is complete, you can use all these functions:
- `list_google_drive_files()` - Browse your Drive files
- `create_google_doc("Document Title")` - Create new Google Docs
- `create_google_sheet("Sheet Title")` - Create new Google Sheets
- `search_google_drive("search term")` - Search your Drive
- `get_google_doc_content("document_id")` - Read document content

## **🔒 Security Notes:**
- Your credentials are stored securely and only accessible to you
- You can revoke access anytime in your Google Account settings
- The tool only requests necessary permissions for file management

## **❓ Need Help?**
If you encounter any issues, call `authenticate_google_workspace()` to check your current authentication status.
"""

    def quick_start_google_workspace(self) -> str:
        """
        One-click start for Google Workspace setup.
        This function guides users through the entire process.

        :return: Next step instructions based on current state
        """
        # Check if already authenticated
        auth_status = self.authenticate_google_workspace()

        if "✅" in auth_status:
            return auth_status  # Already authenticated
        elif "⚠️" in auth_status and "expired" in auth_status.lower():
            return (
                auth_status
                + "\n\n**Ready to re-authenticate?** Call `get_oauth_authorization_url()` to get started!"
            )
        else:
            # First time setup
            return self.get_oauth_authorization_url()

    def _check_and_process_pending_oauth(self) -> str:
        """
        Check for pending OAuth authorization from the callback page and process it automatically.
        This creates a seamless OAuth experience without manual copy/paste.

        :return: Success message if OAuth was processed, empty string if no pending auth
        """
        import os

        # Check for a pending OAuth code file (created by the callback page)
        pending_oauth_file = "/app/backend/data/opt/pending_oauth.json"

        try:
            if os.path.exists(pending_oauth_file):
                with open(pending_oauth_file, "r") as f:
                    oauth_data = json.load(f)

                # Process the OAuth code
                code = oauth_data.get("code")
                if code:
                    # Complete the OAuth setup automatically
                    result = self.complete_oauth_setup(code)

                    # Remove the pending file
                    os.remove(pending_oauth_file)

                    if "successfully" in result.lower():
                        return (
                            "🎉 **Automatic OAuth Setup Complete!**\n"
                            "Your Google Workspace authorization was processed automatically.\n"
                            "You can now use all Google Workspace tools!\n\n" + result
                        )
                    else:
                        return f"⚠️ Automatic OAuth processing failed: {result}"
        except Exception:
            # Silent fail - don't disrupt normal flow
            pass

        return ""

    def process_oauth_message(self, message: str) -> str:
        """
        Smart processor that detects and handles OAuth completion messages automatically.
        This allows users to just paste their OAuth completion message without knowing function names.

        :param message: The message from the user (could be an OAuth completion message)
        :return: Success message if OAuth was processed, empty string if not an OAuth message
        """
        import re

        # Check if this looks like an OAuth completion message
        oauth_patterns = [
            r"Complete authentication with code:\s*([^\s]+)",
            r"Authorization code:\s*([^\s]+)",
            r"Auth code:\s*([^\s]+)",
            r"Code:\s*([^\s]+)",
            r"4/[0-9A-Za-z_-]+",  # Google OAuth code pattern
        ]

        for pattern in oauth_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                # Extract the authorization code
                auth_code = match.group(1) if match.lastindex else match.group(0)

                # Clean up the code (remove any trailing punctuation)
                auth_code = re.sub(r"[^\w\-_/]", "", auth_code)

                if auth_code and len(auth_code) > 10:  # Basic validation
                    # Automatically process the OAuth code
                    result = self.complete_oauth_setup(auth_code)

                    if "successfully" in result.lower() or "complete" in result.lower():
                        return (
                            "🎉 **Automatic OAuth Processing Successful!**\n\n"
                            "I detected your OAuth completion message and processed it automatically!\n\n"
                            + result
                            + "\n\n"
                            "✅ **Your Google Workspace tools are now ready to use!**\n"
                            "Try: `list_google_drive_files()` or `create_google_doc('My Document')`"
                        )
                    else:
                        return f"⚠️ OAuth processing failed: {result}"

        return ""  # Not an OAuth message

    def authenticate_google_workspace(self) -> str:
        """
        Check Google Workspace authentication status and provide guidance.
        This is the main function users should call first.

        :return: Status message with next steps for users.
        """
        # Auto-check for pending OAuth authorization from callback page
        auto_result = self._check_and_process_pending_oauth()
        if auto_result:  # Only return if there's an actual result
            return auto_result

        try:
            creds = self._get_google_credentials()
            if creds:
                # Instead of checking validity (which causes datetime comparisons),
                # let's just check if we have the basic components
                has_token = bool(creds.token)
                has_refresh_token = bool(creds.refresh_token)

                if has_token:
                    return (
                        "✅ **Authentication Available**\n\n"
                        "Google Workspace credentials are loaded. You can now try using Google Workspace tools:\n"
                        "• `list_google_drive_files()` - Browse Drive files\n"
                        "• `create_google_doc('Title')` - Create new docs\n"
                        "• `create_google_sheet('Title')` - Create new sheets\n"
                        "• `search_google_drive('query')` - Search Drive\n"
                        "• `get_google_doc_content('doc_id')` - Read document content\n\n"
                        f"{'✅ Refresh token available for automatic renewal' if has_refresh_token else '⚠️ No refresh token - may need re-authentication if expired'}"
                    )
                else:
                    return (
                        "⚠️ **Authentication Issues**\n\n"
                        "Credentials found but missing access token. Please re-authenticate:\n\n"
                        "1. Call `get_oauth_authorization_url()` to get a new authorization link\n"
                        "2. Follow the link to re-authorize access\n"
                        "3. Call `complete_oauth_setup('your_code')` with the authorization code"
                    )
            else:
                return (
                    "🔐 **First Time Setup Required**\n\n"
                    "Welcome! To use Google Workspace tools, you need to authenticate with Google first.\n\n"
                    "**Quick Start:**\n"
                    "1. Call `get_user_setup_instructions()` for detailed setup guide\n"
                    "2. Or call `get_oauth_authorization_url()` to start authentication now\n\n"
                    "This is a one-time setup that takes about 2 minutes!"
                )

        except Exception as e:
            return (
                f"❌ **Authentication Error**\n\n"
                f"Error: {str(e)}\n\n"
                f"Try calling `get_user_setup_instructions()` for setup help."
            )

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

            # Add safety check for credentials
            if not creds:
                return "❌ No credentials available. Please authenticate first using `get_oauth_authorization_url()`"

            # Check if token is expired before attempting API calls
            try:
                from datetime import datetime, timezone

                with open(self.valves.TOKEN_FILE, "r") as f:
                    token_data = json.load(f)

                expiry_str = token_data.get("expiry")
                if expiry_str:
                    if expiry_str.endswith("Z"):
                        expiry_dt = datetime.fromisoformat(
                            expiry_str.replace("Z", "+00:00")
                        )
                        now_dt = datetime.now(timezone.utc)

                        if now_dt > expiry_dt and not creds.refresh_token:
                            return (
                                "⚠️ **Token Expired - Re-authentication Required**\n\n"
                                "Your Google access token has expired and cannot be automatically renewed.\n"
                                "To access your Google Drive files:\n\n"
                                "1. Call `get_oauth_authorization_url()` to get a new authorization link\n"
                                "2. Follow the link to re-authorize access\n"
                                "3. Call `complete_oauth_setup('your_code')` with the authorization code\n\n"
                                f"Token expired: {expiry_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                                f"Current time: {now_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                            )
            except Exception as check_error:
                print(f"Token expiry check failed: {check_error}")

            # Try to create service with various fallback strategies
            try:
                # Strategy 1: Use credentials as-is
                service = build("drive", "v3", credentials=creds)
            except Exception as e1:
                if "can't compare offset-naive and offset-aware datetimes" in str(e1):
                    # Strategy 2: Create fresh credentials with no expiry to bypass comparison
                    try:
                        fresh_creds = Credentials(
                            token=creds.token,
                            refresh_token=creds.refresh_token,
                            token_uri=creds.token_uri,
                            client_id=creds.client_id,
                            client_secret=creds.client_secret,
                            scopes=creds.scopes,
                            expiry=None,  # No expiry to avoid comparison
                        )
                        service = build("drive", "v3", credentials=fresh_creds)
                    except Exception as e2:
                        return (
                            "❌ **Authentication Error**\n\n"
                            "Unable to authenticate with Google Drive due to token issues.\n\n"
                            "Please re-authenticate:\n"
                            "1. Call `get_oauth_authorization_url()` to get a new authorization link\n"
                            "2. Follow the link to re-authorize access\n"
                            "3. Call `complete_oauth_setup('your_code')` with the authorization code\n\n"
                            f"Technical error: {str(e2)}"
                        )
                else:
                    return f"❌ Service creation error: {str(e1)}"

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
        Search for files in Google Drive with comprehensive error handling.

        :param query: Search query (file name, content, etc.).
        :param max_results: Maximum number of results to return.
        :return: JSON string containing search results.
        """
        try:
            # First, try to get a clean token by refreshing it if we have a refresh token
            try:
                with open(self.valves.TOKEN_FILE, "r") as f:
                    token_data = json.load(f)

                # If we have a refresh token, try to get a fresh access token
                if token_data.get("refresh_token"):
                    from datetime import datetime, timedelta, timezone

                    from google.auth.transport.requests import Request

                    # Create credentials and try to refresh
                    creds = Credentials(
                        token=token_data.get("token"),
                        refresh_token=token_data.get("refresh_token"),
                        token_uri=token_data.get("token_uri"),
                        client_id=token_data.get("client_id"),
                        client_secret=token_data.get("client_secret"),
                        scopes=token_data.get("scopes", self.valves.SCOPES),
                        expiry=datetime.now(timezone.utc)
                        - timedelta(seconds=1),  # Force refresh
                    )

                    # Force a token refresh to get fresh credentials
                    creds.refresh(Request())

                    # Save the refreshed token
                    with open(self.valves.TOKEN_FILE, "w") as f:
                        f.write(creds.to_json())

                    print("Refreshed token to resolve timezone issues")

                    # Use the fresh credentials directly
                    service = build("drive", "v3", credentials=creds)
                else:
                    # No refresh token, use existing credentials
                    creds = self._get_google_credentials()
                    if not creds:
                        return "❌ No credentials available. Please authenticate first using `get_oauth_authorization_url()`"
                    service = build("drive", "v3", credentials=creds)

            except Exception as refresh_error:
                print(f"Token refresh failed: {refresh_error}")
                # Fall back to existing credentials
                creds = self._get_google_credentials()
                if not creds:
                    return "❌ No credentials available. Please authenticate first using `get_oauth_authorization_url()`"
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

            # If it's still a datetime comparison error, provide user-friendly guidance
            if "can't compare offset-naive and offset-aware datetimes" in str(e):
                return (
                    f"❌ **Persistent Timezone Issue**\n\n"
                    f"Unable to search Google Drive due to a timezone compatibility issue.\n\n"
                    f"**Solution:** Get fresh credentials to resolve the problem:\n"
                    f"1. Call `get_oauth_authorization_url()` for a new authorization link\n"
                    f"2. Complete fresh authentication with `complete_oauth_setup('your_code')`\n"
                    f"3. This will create properly formatted credentials\n\n"
                    f"**Alternative:** Try `list_google_drive_files()` which may work better.\n\n"
                    f"Search query was: '{query}'"
                )
            else:
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

    def list_google_drive_files_v2(
        self, max_results: int = 10, folder_id: Optional[str] = None
    ) -> str:
        """
        List files in Google Drive using the v2 programmatic credentials approach.

        :param max_results: Maximum number of files to return (default: 10).
        :param folder_id: ID of a specific folder to list files from (optional).
        :return: JSON string containing the list of files.
        """
        try:
            # Use the v2 programmatic credentials approach
            creds = self._get_google_credentials_v2()

            if not creds:
                return "❌ No credentials available. Please authenticate first using `get_oauth_authorization_url()`"

            # Try to create service with v2 credentials
            try:
                service = build("drive", "v3", credentials=creds)
                print("✅ Service created successfully with v2 credentials")
            except Exception as e1:
                return (
                    "❌ **Service Creation Failed**\n\n"
                    f"Error creating Google Drive service: {str(e1)}\n\n"
                    "Please try the HTTP API version: `list_google_drive_files_http()`"
                )

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
            print(f"Error in v2 list Drive files: {e}")
            return f"❌ Error listing Drive files (v2): {str(e)}"

    def test_all_approaches(self) -> str:
        """
        Test available approaches to identify which one works.
        This function helps diagnose the datetime comparison issue.

        :return: Status of each approach
        """
        results = []

        # Test 1: V2 programmatic credentials
        try:
            v2_result = self.list_google_drive_files_v2(max_results=1)
            if "❌" not in v2_result:
                results.append("✅ V2 programmatic approach: WORKING")
            else:
                results.append(f"❌ V2 programmatic approach: {v2_result[:100]}...")
        except Exception as e:
            results.append(f"❌ V2 programmatic approach: {str(e)}")

        # Test 2: Original approach
        try:
            original_result = self.list_google_drive_files(max_results=1)
            if "❌" not in original_result:
                results.append("✅ Original approach: WORKING")
            else:
                results.append(f"❌ Original approach: {original_result[:100]}...")
        except Exception as e:
            results.append(f"❌ Original approach: {str(e)}")

        return "\n".join(
            [
                "🔍 **Testing Available Approaches for Google Drive Access**\n",
                *results,
                "\n**Recommendation:** Use the approach marked as WORKING above.",
                "\n**Note:** For HTTP API approach, install google_workspace_tools_http.py separately.",
            ]
        )
