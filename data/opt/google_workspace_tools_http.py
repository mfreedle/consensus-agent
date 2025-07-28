"""
title: Google Workspace Tools (HTTP API Version)
author: rthidden
author_url: https://hiddendigitalaix.com
git_url: https://github.com/rthidden/google-workspace-tools.git
description: This tool provides comprehensive Google Workspace functionality using direct HTTP API calls to bypass datetime comparison issues.
required_open_webui_version: 0.6.18
requirements: google-auth, google-auth-oauthlib, requests
version: 2.0.0
licence: MIT
"""

import json
import os
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests
from pydantic import BaseModel, Field


class Tools:
    def __init__(self):
        """Initialize the Google Workspace Tools with HTTP API approach."""
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
            default="http://localhost:19328/oauth-callback",
            description="OAuth redirect URI - simple path, code will be in URL",
        )
        SCOPES: List[str] = Field(
            default=[
                # Google Drive APIs
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive.metadata",
                "https://www.googleapis.com/auth/drive.photos.readonly",
                # Google Workspace Document APIs
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/presentations",
                # Gmail APIs
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.modify",
                # Calendar APIs
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
                "https://www.googleapis.com/auth/calendar.readonly",
                # Contacts & People APIs
                "https://www.googleapis.com/auth/contacts",
                "https://www.googleapis.com/auth/contacts.readonly",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                # Tasks API
                "https://www.googleapis.com/auth/tasks",
                "https://www.googleapis.com/auth/tasks.readonly",
                # YouTube APIs
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtubepartner",
                "https://www.googleapis.com/auth/yt-analytics.readonly",
                "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
                # NOTE: Google Keep API is NOT AVAILABLE for third-party OAuth apps
                # Google Keep requires special approval and is restricted to internal use
                # "https://www.googleapis.com/auth/keep",
                # "https://www.googleapis.com/auth/keep.readonly",
            ],
            description="Comprehensive Google API scopes for all enabled APIs",
        )

    def _get_access_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary."""
        try:
            if not os.path.exists(self.valves.TOKEN_FILE):
                return None

            with open(self.valves.TOKEN_FILE, "r") as f:
                token_data = json.load(f)

            # Check if token exists
            access_token = token_data.get("token")
            if not access_token:
                return None

            # Check expiry
            expiry_str = token_data.get("expiry")
            if expiry_str:
                try:
                    if expiry_str.endswith("Z"):
                        expiry_dt = datetime.fromisoformat(
                            expiry_str.replace("Z", "+00:00")
                        )
                    else:
                        expiry_dt = datetime.fromisoformat(expiry_str)

                    now_dt = datetime.now(timezone.utc)

                    # If token is expired and we have refresh token, refresh it
                    if now_dt >= expiry_dt and token_data.get("refresh_token"):
                        print("Token expired, refreshing...")
                        return self._refresh_token(token_data)
                except Exception as e:
                    print(f"Error parsing expiry time: {e}")

            return access_token

        except Exception as e:
            print(f"Error getting access token: {e}")
            return None

    def _refresh_token(self, token_data: dict) -> Optional[str]:
        """Refresh the access token using the refresh token."""
        try:
            refresh_url = "https://oauth2.googleapis.com/token"
            refresh_data = {
                "client_id": token_data.get("client_id"),
                "client_secret": token_data.get("client_secret"),
                "refresh_token": token_data.get("refresh_token"),
                "grant_type": "refresh_token",
            }

            response = requests.post(refresh_url, data=refresh_data)

            if response.status_code == 200:
                new_token_data = response.json()

                # Update the stored token
                token_data.update(
                    {
                        "token": new_token_data["access_token"],
                        "expiry": (
                            datetime.now(timezone.utc)
                            + timedelta(seconds=new_token_data.get("expires_in", 3600))
                        )
                        .isoformat()
                        .replace("+00:00", "Z"),
                    }
                )

                # Save updated token
                with open(self.valves.TOKEN_FILE, "w") as f:
                    json.dump(token_data, f, indent=2)

                print("Token refreshed successfully")
                return new_token_data["access_token"]
            else:
                print(f"Token refresh failed: {response.text}")
                return None

        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None

    def _make_api_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make a direct HTTP API request to Google APIs."""
        access_token = self._get_access_token()
        if not access_token:
            return {
                "error": "No valid access token available. Please authenticate first."
            }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}

            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": f"API request failed: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {"error": f"Request error: {str(e)}"}

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
                f"🎉 After authorization, you'll be redirected to: `http://localhost:19328/oauth-callback?code=YOUR_CODE`\n"
                f"📋 The page will show 'Not Found' (that's expected!) - just copy the authorization code from the URL bar.\n"
                f"✨ Copy the code and use the 'complete_oauth_setup' function.\n\n"
                f"You may then close the tab and go outside and play! 🌟"
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

                # Create the token file with proper timezone-aware expiry
                expiry_time = datetime.now(timezone.utc) + timedelta(
                    seconds=token_info.get("expires_in", 3600)
                )
                token_file_data = {
                    "token": token_info["access_token"],
                    "refresh_token": token_info.get("refresh_token"),
                    "token_uri": token_url,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scopes": self.valves.SCOPES,
                    "expiry": expiry_time.isoformat().replace("+00:00", "Z"),
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

    def authenticate_google_workspace(self) -> str:
        """
        Check Google Workspace authentication status and provide guidance.
        This is the main function users should call first.

        :return: Status message with next steps for users.
        """
        try:
            access_token = self._get_access_token()
            if access_token:
                return (
                    "✅ **Authentication Available**\n\n"
                    "Google Workspace credentials are loaded. You can now try using Google Workspace tools:\n"
                    "• `list_google_drive_files_http()` - Browse Drive files\n"
                    "• `create_google_doc_http('Title')` - Create new docs\n"
                    "• `search_google_drive_http('query')` - Search Drive\n"
                    "• `get_google_doc_content_http('doc_id')` - Read document content\n\n"
                    "Using direct HTTP API calls (no datetime comparison issues!)"
                )
            else:
                return (
                    "🔐 **First Time Setup Required**\n\n"
                    "Welcome! To use Google Workspace tools, you need to authenticate with Google first.\n\n"
                    "**Quick Start:**\n"
                    "1. Call `get_oauth_authorization_url()` to start authentication\n"
                    "2. Or call `get_user_setup_instructions()` for detailed setup guide\n\n"
                    "This is a one-time setup that takes about 2 minutes!"
                )

        except Exception as e:
            return (
                f"❌ **Authentication Error**\n\n"
                f"Error: {str(e)}\n\n"
                f"Try calling `get_oauth_authorization_url()` for setup help."
            )

    def list_google_drive_files_http(
        self,
        max_results: int = 10,
        folder_id: Optional[str] = None,
        personal_drive_only: bool = True,
    ) -> str:
        """
        List files in Google Drive using direct HTTP API calls.

        :param max_results: Maximum number of files to return (default: 10).
        :param folder_id: ID of a specific folder to list files from (optional).
        :param personal_drive_only: If True, only show files from personal drive, not shared drives (default: True).
        :return: JSON string containing the list of files.
        """
        try:
            url = "https://www.googleapis.com/drive/v3/files"
            params = {
                "pageSize": max_results,
                "fields": "nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink, ownedByMe, shared, driveId)",
            }

            # Build query to filter files
            query_parts = []

            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")

            if personal_drive_only:
                # Only show files in the user's personal drive (not shared drives)
                query_parts.append("'me' in owners")

            if query_parts:
                params["q"] = " and ".join(query_parts)

            result = self._make_api_request(url, "GET", params=params)

            if "error" in result:
                return f"❌ Error listing Drive files: {result['error']}"

            items = result.get("files", [])

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
                        "ownedByMe": item.get("ownedByMe", False),
                        "shared": item.get("shared", False),
                        "driveId": item.get("driveId", "personal"),
                        "driveType": "Personal Drive"
                        if not item.get("driveId")
                        else "Shared Drive",
                    }
                )

            return json.dumps(files_data, indent=2)

        except Exception as e:
            return f"❌ Error listing Drive files: {str(e)}"

    def search_google_drive_http(
        self, query: str, max_results: int = 10, personal_drive_only: bool = True
    ) -> str:
        """
        Search for files in Google Drive using direct HTTP API calls.

        :param query: Search query (file name, content, etc.).
        :param max_results: Maximum number of results to return.
        :param personal_drive_only: If True, only search in personal drive, not shared drives (default: True).
        :return: JSON string containing search results.
        """
        try:
            url = "https://www.googleapis.com/drive/v3/files"

            # Build search query
            search_query = f"name contains '{query}' or fullText contains '{query}'"
            if personal_drive_only:
                search_query += " and 'me' in owners"

            params = {
                "q": search_query,
                "pageSize": max_results,
                "fields": "nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink, ownedByMe, shared, driveId)",
            }

            result = self._make_api_request(url, "GET", params=params)

            if "error" in result:
                return f"❌ Error searching Drive: {result['error']}"

            items = result.get("files", [])

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
                        "ownedByMe": item.get("ownedByMe", False),
                        "shared": item.get("shared", False),
                        "driveId": item.get("driveId", "personal"),
                        "driveType": "Personal Drive"
                        if not item.get("driveId")
                        else "Shared Drive",
                    }
                )

            return json.dumps(files_data, indent=2)

        except Exception as e:
            return f"❌ Error searching Drive: {str(e)}"

    def list_personal_drive_files_only_http(self, max_results: int = 10) -> str:
        """
        List files ONLY from the user's personal Google Drive (excludes all shared drives).
        This is equivalent to browsing https://drive.google.com/drive/u/0/my-drive

        :param max_results: Maximum number of files to return (default: 10).
        :return: JSON string containing the list of personal drive files only.
        """
        try:
            url = "https://www.googleapis.com/drive/v3/files"
            params = {
                "pageSize": max_results,
                "q": "'me' in owners and trashed=false",  # Only files owned by the user, not trashed
                "fields": "nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink, ownedByMe, parents)",
                "orderBy": "modifiedTime desc",  # Show most recently modified first
            }

            result = self._make_api_request(url, "GET", params=params)

            if "error" in result:
                return f"❌ Error listing personal drive files: {result['error']}"

            items = result.get("files", [])

            if not items:
                return "No files found in your personal drive."

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
                        "ownedByMe": True,  # Always true for this function
                        "driveType": "Personal Drive",
                        "canEdit": True,  # User owns these files, so can edit
                    }
                )

            return json.dumps(files_data, indent=2)

        except Exception as e:
            return f"❌ Error listing personal drive files: {str(e)}"

    def create_google_doc_http(self, title: str, content: str = "") -> str:
        """
        Create a new Google Document using direct HTTP API calls.

        :param title: The title of the document.
        :param content: Initial content for the document (optional).
        :return: Document ID and view link.
        """
        try:
            # Create the document
            docs_url = "https://docs.googleapis.com/v1/documents"
            doc_data = {"title": title}

            result = self._make_api_request(docs_url, "POST", doc_data)

            if "error" in result:
                return f"❌ Error creating document: {result['error']}"

            doc_id = result["documentId"]

            # Add content if provided
            if content:
                batch_update_url = (
                    f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
                )
                requests_data = {
                    "requests": [
                        {"insertText": {"location": {"index": 1}, "text": content}}
                    ]
                }

                batch_result = self._make_api_request(
                    batch_update_url, "POST", requests_data
                )
                if "error" in batch_result:
                    print(f"Warning: Error adding content: {batch_result['error']}")

            # Get the document link
            drive_url = f"https://www.googleapis.com/drive/v3/files/{doc_id}"
            params = {"fields": "webViewLink"}

            link_result = self._make_api_request(drive_url, "GET", params=params)
            web_view_link = link_result.get("webViewLink", "No link available")

            result_data = {
                "documentId": doc_id,
                "title": title,
                "webViewLink": web_view_link,
            }

            return json.dumps(result_data, indent=2)

        except Exception as e:
            return f"❌ Error creating Google Doc: {str(e)}"

    def get_google_doc_content_http(self, document_id: str) -> str:
        """
        Get the content of a Google Document using direct HTTP API calls.

        :param document_id: The ID of the document.
        :return: The text content of the document.
        """
        try:
            url = f"https://docs.googleapis.com/v1/documents/{document_id}"

            result = self._make_api_request(url, "GET")

            if "error" in result:
                return f"❌ Error getting document: {result['error']}"

            content = result.get("body", {}).get("content", [])

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
            return f"❌ Error getting Google Doc content: {str(e)}"

    def edit_google_doc_http(
        self, document_id: str, text_to_add: str, location: str = "end"
    ) -> str:
        """
        Edit a Google Document by adding text at the specified location.
        First checks permissions and provides alternatives if editing is not allowed.

        :param document_id: The ID of the document to edit.
        :param text_to_add: The text to add to the document.
        :param location: Where to add text - "start", "end", or specific index number.
        :return: Status message indicating success or failure.
        """
        try:
            # First check if we have edit permissions
            drive_url = f"https://www.googleapis.com/drive/v3/files/{document_id}"
            params = {"fields": "id,name,capabilities"}

            perm_result = self._make_api_request(drive_url, "GET", params=params)

            if "error" in perm_result:
                return f"❌ Error checking permissions: {perm_result['error']}"

            capabilities = perm_result.get("capabilities", {})
            can_edit = capabilities.get("canEdit", False)
            can_comment = capabilities.get("canComment", False)
            doc_name = perm_result.get("name", "Unknown Document")

            if not can_edit:
                # If we can't edit, provide helpful alternatives
                alternatives = []
                if can_comment:
                    alternatives.append(
                        "• Add a comment: `add_comment_to_doc_http(document_id, 'Your comment')`"
                    )
                alternatives.append("• Request edit access from the document owner")
                alternatives.append(
                    "• Create a copy you can edit: `copy_google_doc_http(document_id, 'New Title')`"
                )

                return (
                    f"❌ **Edit Permission Denied for '{doc_name}'**\n\n"
                    f"You don't have edit permissions for this document.\n\n"
                    f"**Available alternatives:**\n" + "\n".join(alternatives) + "\n\n"
                    f"**Document capabilities:**\n"
                    f"• Can edit: {can_edit}\n"
                    f"• Can comment: {can_comment}\n"
                    f"• Can copy: {capabilities.get('canCopy', False)}"
                )

            # Get document to find insertion point
            doc_url = f"https://docs.googleapis.com/v1/documents/{document_id}"
            doc_result = self._make_api_request(doc_url, "GET")

            if "error" in doc_result:
                return f"❌ Error accessing document: {doc_result['error']}"

            # Calculate insertion index
            if location == "start":
                index = 1
            elif location == "end":
                # Find the end of the document
                content = doc_result.get("body", {}).get("content", [])
                index = 1
                for element in content:
                    if "endIndex" in element:
                        index = max(index, element["endIndex"] - 1)
            else:
                try:
                    index = int(location)
                except ValueError:
                    return f"❌ Invalid location '{location}'. Use 'start', 'end', or a number."

            # Perform the edit
            batch_update_url = (
                f"https://docs.googleapis.com/v1/documents/{document_id}:batchUpdate"
            )
            requests_data = {
                "requests": [
                    {"insertText": {"location": {"index": index}, "text": text_to_add}}
                ]
            }

            result = self._make_api_request(batch_update_url, "POST", requests_data)

            if "error" in result:
                return f"❌ Error editing document: {result['error']}"

            return (
                f"✅ **Document Edited Successfully**\n\n"
                f"Document: {doc_name}\n"
                f"Added text at: {location}\n"
                f"Characters added: {len(text_to_add)}\n"
                f"Preview: {text_to_add[:100]}{'...' if len(text_to_add) > 100 else ''}"
            )

        except Exception as e:
            return f"❌ Error editing Google Doc: {str(e)}"

    def replace_text_in_doc_http(
        self, document_id: str, old_text: str, new_text: str
    ) -> str:
        """
        Replace specific text in a Google Document.

        :param document_id: The ID of the document to edit.
        :param old_text: The text to find and replace.
        :param new_text: The text to replace it with.
        :return: Status message indicating success or failure.
        """
        try:
            batch_update_url = (
                f"https://docs.googleapis.com/v1/documents/{document_id}:batchUpdate"
            )
            requests_data = {
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {"text": old_text, "matchCase": False},
                            "replaceText": new_text,
                        }
                    }
                ]
            }

            result = self._make_api_request(batch_update_url, "POST", requests_data)

            if "error" in result:
                return f"❌ Error replacing text: {result['error']}"

            # Check if any replacements were made
            replacements = (
                result.get("replies", [{}])[0]
                .get("replaceAllText", {})
                .get("occurrencesChanged", 0)
            )

            if replacements > 0:
                return f"✅ Successfully replaced {replacements} occurrence(s) of '{old_text}' with '{new_text}'."
            else:
                return f"⚠️ No occurrences of '{old_text}' found in the document."

        except Exception as e:
            return f"❌ Error replacing text in document: {str(e)}"

    def format_text_in_doc_http(
        self, document_id: str, text: str, format_type: str
    ) -> str:
        """
        Apply formatting to specific text in a Google Document.

        :param document_id: The ID of the document to format.
        :param text: The text to format.
        :param format_type: Type of formatting - "bold", "italic", "underline".
        :return: Status message indicating success or failure.
        """
        try:
            # First find the text in the document
            doc_url = f"https://docs.googleapis.com/v1/documents/{document_id}"
            doc_result = self._make_api_request(doc_url, "GET")

            if "error" in doc_result:
                return f"❌ Error accessing document: {doc_result['error']}"

            # Apply formatting
            batch_update_url = (
                f"https://docs.googleapis.com/v1/documents/{document_id}:batchUpdate"
            )

            format_request = {}
            if format_type.lower() == "bold":
                format_request = {"bold": True}
            elif format_type.lower() == "italic":
                format_request = {"italic": True}
            elif format_type.lower() == "underline":
                format_request = {"underline": True}
            else:
                return f"❌ Unsupported format type '{format_type}'. Use 'bold', 'italic', or 'underline'."

            requests_data = {
                "requests": [
                    {
                        "updateTextStyle": {
                            "range": {
                                "startIndex": 1,
                                "endIndex": -1,  # This will need to be refined for specific text
                            },
                            "textStyle": format_request,
                            "fields": list(format_request.keys())[0],
                        }
                    }
                ]
            }

            result = self._make_api_request(batch_update_url, "POST", requests_data)

            if "error" in result:
                return f"❌ Error formatting text: {result['error']}"

            return f"✅ Successfully applied {format_type} formatting to document."

        except Exception as e:
            return f"❌ Error formatting document: {str(e)}"

    def add_comment_to_doc_http(
        self, document_id: str, comment_text: str, anchor_text: Optional[str] = None
    ) -> str:
        """
        Add a comment to a Google Document using direct HTTP API calls.
        This works even when you don't have edit permissions but have comment permissions.

        :param document_id: The ID of the document to comment on.
        :param comment_text: The text of the comment to add.
        :param anchor_text: Optional text to anchor the comment to (if not provided, adds general comment).
        :return: Status message indicating success or failure.
        """
        try:
            # First check if we can comment
            drive_url = f"https://www.googleapis.com/drive/v3/files/{document_id}"
            params = {"fields": "id,name,capabilities"}

            perm_result = self._make_api_request(drive_url, "GET", params=params)
            if "error" in perm_result:
                return f"❌ Error checking permissions: {perm_result['error']}"

            can_comment = perm_result.get("capabilities", {}).get("canComment", False)
            if not can_comment:
                return "❌ You don't have permission to comment on this document."

            # Create comment using Drive API comments endpoint
            comments_url = (
                f"https://www.googleapis.com/drive/v3/files/{document_id}/comments"
            )
            comment_data = {
                "content": comment_text,
            }

            result = self._make_api_request(comments_url, "POST", comment_data)

            if "error" in result:
                return f"❌ Error adding comment: {result['error']}"

            comment_id = result.get("id", "unknown")
            return f"✅ Comment added successfully! Comment ID: {comment_id}"

        except Exception as e:
            return f"❌ Error adding comment: {str(e)}"

    def copy_google_doc_http(self, document_id: str, new_title: str) -> str:
        """
        Create a copy of a Google Document that you can edit.

        :param document_id: The ID of the document to copy.
        :param new_title: The title for the new copy.
        :return: Information about the copied document.
        """
        try:
            # Create copy using Drive API
            copy_url = f"https://www.googleapis.com/drive/v3/files/{document_id}/copy"
            copy_data = {
                "name": new_title,
                "parents": [],  # Will be placed in root of My Drive
            }

            result = self._make_api_request(copy_url, "POST", copy_data)

            if "error" in result:
                return f"❌ Error copying document: {result['error']}"

            new_doc_id = result.get("id")
            new_doc_name = result.get("name")

            # Get the web view link
            drive_url = f"https://www.googleapis.com/drive/v3/files/{new_doc_id}"
            params = {"fields": "webViewLink"}
            link_result = self._make_api_request(drive_url, "GET", params=params)
            web_view_link = link_result.get("webViewLink", "No link available")

            return (
                f"✅ **Document Copied Successfully**\n\n"
                f"New Document: {new_doc_name}\n"
                f"Document ID: {new_doc_id}\n"
                f"Link: {web_view_link}\n\n"
                f"You now have full edit permissions on this copy!"
            )

        except Exception as e:
            return f"❌ Error copying document: {str(e)}"

    def check_document_permissions_http(self, document_id: str) -> str:
        """
        Check what permissions you have for a specific document.

        :param document_id: The ID of the document to check.
        :return: Detailed permissions information.
        """
        try:
            drive_url = f"https://www.googleapis.com/drive/v3/files/{document_id}"
            params = {"fields": "id,name,capabilities,owners,permissions"}

            result = self._make_api_request(drive_url, "GET", params=params)

            if "error" in result:
                return f"❌ Error checking permissions: {result['error']}"

            name = result.get("name", "Unknown Document")
            capabilities = result.get("capabilities", {})

            # Format the permissions nicely
            permissions_info = [
                f"📄 **Document**: {name}",
                f"🆔 **ID**: {document_id}",
                "",
                "🔐 **Your Permissions**:",
                f"• Can edit: {'✅' if capabilities.get('canEdit') else '❌'}",
                f"• Can comment: {'✅' if capabilities.get('canComment') else '❌'}",
                f"• Can view: {'✅' if capabilities.get('canReadRevisions') else '❌'}",
                f"• Can copy: {'✅' if capabilities.get('canCopy') else '❌'}",
                f"• Can download: {'✅' if capabilities.get('canDownload') else '❌'}",
                f"• Can share: {'✅' if capabilities.get('canShare') else '❌'}",
                "",
                "💡 **Available Actions**:",
            ]

            # Add suggestions based on permissions
            if capabilities.get("canEdit"):
                permissions_info.append("• Edit document: `edit_google_doc_http()`")
            if capabilities.get("canComment"):
                permissions_info.append("• Add comments: `add_comment_to_doc_http()`")
            if capabilities.get("canCopy"):
                permissions_info.append(
                    "• Create editable copy: `copy_google_doc_http()`"
                )

            return "\n".join(permissions_info)

        except Exception as e:
            return f"❌ Error checking permissions: {str(e)}"

    def create_google_sheet_http(
        self, title: str, data: Optional[List[List[str]]] = None
    ) -> str:
        """
        Create a new Google Spreadsheet using direct HTTP API calls.

        :param title: The title of the spreadsheet.
        :param data: Initial data for the spreadsheet as a list of rows (optional).
        :return: Spreadsheet ID and view link.
        """
        try:
            # Create the spreadsheet
            sheets_url = "https://sheets.googleapis.com/v4/spreadsheets"
            sheet_data = {"properties": {"title": title}}

            result = self._make_api_request(sheets_url, "POST", sheet_data)

            if "error" in result:
                return f"❌ Error creating spreadsheet: {result['error']}"

            spreadsheet_id = result["spreadsheetId"]

            # Add data if provided
            if data:
                values_url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A1"
                params = {"valueInputOption": "RAW"}
                values_data = {"values": data}

                values_result = self._make_api_request(
                    values_url, "PUT", values_data, params
                )
                if "error" in values_result:
                    print(f"Warning: Error adding data: {values_result['error']}")

            # Get the spreadsheet link
            drive_url = f"https://www.googleapis.com/drive/v3/files/{spreadsheet_id}"
            params = {"fields": "webViewLink"}

            link_result = self._make_api_request(drive_url, "GET", params=params)
            web_view_link = link_result.get("webViewLink", "No link available")

            result_data = {
                "spreadsheetId": spreadsheet_id,
                "title": title,
                "webViewLink": web_view_link,
            }

            return json.dumps(result_data, indent=2)

        except Exception as e:
            return f"❌ Error creating Google Sheet: {str(e)}"

    def read_google_sheet_data_http(
        self, spreadsheet_id: str, range_name: str = "A1:Z100"
    ) -> str:
        """
        Read data from a Google Spreadsheet using direct HTTP API calls.

        :param spreadsheet_id: The ID of the spreadsheet.
        :param range_name: The range to read (e.g., 'A1:Z100').
        :return: JSON string containing the spreadsheet data.
        """
        try:
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}"

            result = self._make_api_request(url, "GET")

            if "error" in result:
                return f"❌ Error reading spreadsheet: {result['error']}"

            values = result.get("values", [])

            if not values:
                return "No data found in the specified range."

            return json.dumps(values, indent=2)

        except Exception as e:
            return f"❌ Error reading Google Sheet: {str(e)}"

    def update_google_sheet_data_http(
        self, spreadsheet_id: str, range_name: str, data: List[List[str]]
    ) -> str:
        """
        Update data in a Google Spreadsheet using direct HTTP API calls.

        :param spreadsheet_id: The ID of the spreadsheet.
        :param range_name: The range to update (e.g., 'A1:C3').
        :param data: The data to write as a list of rows.
        :return: Status message indicating success or failure.
        """
        try:
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}"
            params = {"valueInputOption": "RAW"}
            values_data = {"values": data}

            result = self._make_api_request(url, "PUT", values_data, params)

            if "error" in result:
                return f"❌ Error updating spreadsheet: {result['error']}"

            updated_cells = result.get("updatedCells", 0)
            return (
                f"✅ Successfully updated {updated_cells} cells in range {range_name}."
            )

        except Exception as e:
            return f"❌ Error updating Google Sheet: {str(e)}"

    def send_email_http(
        self, to: str, subject: str, body: str, from_email: Optional[str] = None
    ) -> str:
        """
        Send an email using Gmail API via direct HTTP calls.

        :param to: Recipient email address.
        :param subject: Email subject.
        :param body: Email body content.
        :param from_email: Sender email (optional, uses authenticated user's email if not provided).
        :return: Status message indicating success or failure.
        """
        try:
            import base64

            # Create the email message
            message = f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}"
            raw_message = base64.urlsafe_b64encode(message.encode()).decode()

            gmail_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            email_data = {"raw": raw_message}

            result = self._make_api_request(gmail_url, "POST", email_data)

            if "error" in result:
                return f"❌ Error sending email: {result['error']}"

            message_id = result.get("id", "Unknown")
            return f"✅ Email sent successfully to {to}. Message ID: {message_id}"

        except Exception as e:
            return f"❌ Error sending email: {str(e)}"

    def list_gmail_messages_http(self, query: str = "", max_results: int = 10) -> str:
        """
        List Gmail messages using direct HTTP API calls.

        :param query: Gmail search query (optional).
        :param max_results: Maximum number of messages to return.
        :return: JSON string containing message list.
        """
        try:
            url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
            params: dict = {"maxResults": max_results}
            if query:
                params["q"] = query

            result = self._make_api_request(url, "GET", params=params)

            if "error" in result:
                return f"❌ Error listing messages: {result['error']}"

            messages = result.get("messages", [])

            if not messages:
                return "No messages found."

            # Get details for each message
            detailed_messages = []
            for msg in messages[:max_results]:
                msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}"
                msg_params = {
                    "format": "metadata",
                    "metadataHeaders": ["From", "To", "Subject", "Date"],
                }

                msg_result = self._make_api_request(msg_url, "GET", params=msg_params)
                if "error" not in msg_result:
                    headers = {
                        h["name"]: h["value"]
                        for h in msg_result.get("payload", {}).get("headers", [])
                    }
                    detailed_messages.append(
                        {
                            "id": msg["id"],
                            "threadId": msg_result.get("threadId"),
                            "from": headers.get("From", "Unknown"),
                            "to": headers.get("To", "Unknown"),
                            "subject": headers.get("Subject", "No Subject"),
                            "date": headers.get("Date", "Unknown"),
                        }
                    )

            return json.dumps(detailed_messages, indent=2)

        except Exception as e:
            return f"❌ Error listing Gmail messages: {str(e)}"

    def create_calendar_event_http(
        self, title: str, start_time: str, end_time: str, description: str = ""
    ) -> str:
        """
        Create a calendar event using direct HTTP API calls.

        :param title: Event title.
        :param start_time: Start time in ISO format (e.g., "2025-07-25T10:00:00").
        :param end_time: End time in ISO format.
        :param description: Event description (optional).
        :return: Status message indicating success or failure.
        """
        try:
            calendar_url = (
                "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            )

            event_data = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "end": {"dateTime": end_time, "timeZone": "UTC"},
            }

            result = self._make_api_request(calendar_url, "POST", event_data)

            if "error" in result:
                return f"❌ Error creating calendar event: {result['error']}"

            event_id = result.get("id", "Unknown")
            html_link = result.get("htmlLink", "No link available")

            return f"✅ Calendar event '{title}' created successfully. Event ID: {event_id}. Link: {html_link}"

        except Exception as e:
            return f"❌ Error creating calendar event: {str(e)}"

    def list_calendar_events_http(self, max_results: int = 10) -> str:
        """
        List upcoming calendar events using direct HTTP API calls.

        :param max_results: Maximum number of events to return.
        :return: JSON string containing events list.
        """
        try:
            calendar_url = (
                "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            )
            params = {
                "maxResults": max_results,
                "orderBy": "startTime",
                "singleEvents": True,
                "timeMin": datetime.now(timezone.utc).isoformat(),
            }

            result = self._make_api_request(calendar_url, "GET", params=params)

            if "error" in result:
                return f"❌ Error listing calendar events: {result['error']}"

            events = result.get("items", [])

            if not events:
                return "No upcoming events found."

            events_data = []
            for event in events:
                events_data.append(
                    {
                        "id": event.get("id"),
                        "summary": event.get("summary", "No Title"),
                        "start": event.get("start", {}).get(
                            "dateTime", event.get("start", {}).get("date")
                        ),
                        "end": event.get("end", {}).get(
                            "dateTime", event.get("end", {}).get("date")
                        ),
                        "description": event.get("description", ""),
                        "htmlLink": event.get("htmlLink", ""),
                    }
                )

            return json.dumps(events_data, indent=2)

        except Exception as e:
            return f"❌ Error listing calendar events: {str(e)}"

    # ==================================================================================
    # ❌ GOOGLE KEEP FUNCTIONS DISABLED - API NOT AVAILABLE FOR THIRD-PARTY OAUTH
    # ==================================================================================
    #
    # Google Keep API requires special approval from Google and is not available
    # for general third-party OAuth applications. The scopes cause OAuth errors.
    #
    # If you need note-taking functionality, consider alternatives like:
    # - Google Docs (create simple text documents)
    # - Google Drive (create text files)
    # - Google Tasks (for task-like notes)
    #
    # Uncomment the functions below only if you have special Google approval.
    # ==================================================================================

    def get_user_setup_instructions(self) -> str:
        """
        Provide complete setup instructions for new users.

        :return: Step-by-step setup guide
        """
        return """# 🚀 **Google Workspace Tools Setup Guide (HTTP API Version)**

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
Once setup is complete, you can use all these comprehensive functions:

#### **📁 Google Drive (Personal Drive Focus):**
- `list_personal_drive_files_only_http()` - Browse ONLY your personal drive files (recommended)
- `list_google_drive_files_http(personal_drive_only=True)` - Browse with personal drive filter
- `search_google_drive_http("search term", personal_drive_only=True)` - Search only personal drive

#### **📝 Google Docs (Full Editing - Personal Drive):**
- `create_google_doc_http("Document Title", "content")` - Create new Google Docs
- `get_google_doc_content_http("document_id")` - Read document content
- `edit_google_doc_http("doc_id", "text to add", "end")` - Add text to YOUR documents
- `replace_text_in_doc_http("doc_id", "old text", "new text")` - Replace text in YOUR documents
- `format_text_in_doc_http("doc_id", "text", "bold")` - Format text (bold/italic/underline)
- `add_comment_to_doc_http("doc_id", "comment")` - Add comments (works on shared docs too)
- `copy_google_doc_http("doc_id", "New Title")` - Copy any doc to your personal drive

#### **📊 Google Sheets:**
- `create_google_sheet_http("Sheet Title", [["row1"], ["row2"]])` - Create new sheets
- `read_google_sheet_data_http("sheet_id", "A1:C10")` - Read sheet data
- `update_google_sheet_data_http("sheet_id", "A1:C3", data)` - Update sheet data

#### **📧 Gmail:**
- `send_email_http("recipient@email.com", "Subject", "Body")` - Send emails
- `list_gmail_messages_http("search query", 10)` - List/search emails

#### **📅 Google Calendar:**
- `create_calendar_event_http("Event Title", "2025-07-25T10:00:00", "2025-07-25T11:00:00")` - Create events
- `list_calendar_events_http(10)` - List upcoming events

#### **❌ Google Keep (Notes) - NOT AVAILABLE:**
**Google Keep API is restricted to internal Google applications and not available for third-party OAuth.**
Use alternatives:
- Google Docs for longer notes
- Google Drive text files for simple notes  
- Google Tasks for task-based notes

## **🆕 What's New - Personal Drive Focus:**
- **Personal Drive Priority** - By default, only shows files you own and can edit
- **Shared Drive Filtering** - Avoids permission issues with organizational shared drives
- **Smart Permission Checking** - Automatically detects what you can do with each document
- **Full Google Docs editing** - Add, replace, and format text in YOUR documents
- **Comment on any document** - Add comments even to shared/read-only documents
- **Copy to edit** - Copy shared documents to your personal drive for full editing
- **All supported APIs** - Drive, Docs, Sheets, Gmail, Calendar, Tasks, YouTube, Contacts
- **Direct HTTP API calls** - No datetime comparison issues
- **Automatic token refresh** - Seamless authentication management

## **🔒 Security & Permissions:**
Your tool now has access to all enabled Google APIs:
- Google Drive API, Google Docs API, Google Sheets API
- Gmail API, Google Calendar API
- Contacts API, People API, Google Tasks API
- YouTube APIs and Analytics
- All permissions handled securely with OAuth 2.0

**Note**: Google Keep API is not available for third-party applications.

## **❓ Need Help?**
If you encounter any issues, call `authenticate_google_workspace()` to check your current authentication status.
"""
