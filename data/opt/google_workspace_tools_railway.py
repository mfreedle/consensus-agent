"""
title: Google Workspace Tools - Railway Deployment
author: rthidden
author_url: https://hiddendigitalaix.com
git_url: https://github.com/rthidden/google-workspace-tools.git
description: Enhanced Google Workspace tools optimized for Railway deployment with persistent database-backed OAuth handling
required_open_webui_version: 0.6.18
requirements: google-auth, google-api-python-client, google-auth-httplib2, google-auth-oauthlib, requests
version: 3.0.0
licence: MIT
"""

import json
import os
import re
import urllib.parse
from typing import List, Optional

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel, Field


class Tools:
    def __init__(self):
        """Initialize the Google Workspace Tools with Railway optimizations."""
        self.valves = self.Valves()
        self.citation = True

        # Ensure Railway environment is properly detected
        self.is_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT"))
        self.railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")

        # Database-first approach for token storage
        self.use_database = True
        # Use existing webui.db for Railway, create test db locally
        if self.is_railway:
            self.db_path = os.environ.get("DATABASE_PATH", "/app/backend/data/webui.db")
        else:
            self.db_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "webui.db"
            )

        # Fallback file paths (for backward compatibility)
        if self.is_railway:
            # Use Railway's persistent volume mount point
            # You need to mount a persistent volume to /data in Railway
            self.base_path = "/data"
            self.token_file = f"{self.base_path}/google_token.json"
            self.credentials_file = f"{self.base_path}/oauth_credentials.json"
            self.pending_oauth_file = f"{self.base_path}/pending_oauth.json"
        else:
            # Local development paths
            self.base_path = "/app/backend/data/opt"
            self.token_file = self.valves.TOKEN_FILE
            self.credentials_file = self.valves.GOOGLE_CREDENTIALS_FILE
            self.pending_oauth_file = f"{self.base_path}/pending_oauth.json"

    def _get_redirect_uri(self) -> str:
        """Get the appropriate redirect URI, auto-detecting Railway environment."""
        # Railway detection
        if self.railway_domain:
            return f"https://{self.railway_domain}/google-oauth-callback.html"

        # Environment variable override
        env_redirect = os.environ.get("GOOGLE_OAUTH_REDIRECT_URI")
        if env_redirect:
            return env_redirect

        # Use configured default
        return self.valves.REDIRECT_URI

    def _ensure_directories(self) -> None:
        """Ensure all necessary directories exist for token storage."""
        directories = [
            os.path.dirname(self.token_file),
            os.path.dirname(self.credentials_file),
            os.path.dirname(self.pending_oauth_file),
        ]

        print(
            f"🔍 Railway Debug - Environment: RAILWAY_ENVIRONMENT={os.environ.get('RAILWAY_ENVIRONMENT')}"
        )
        print("🔍 Railway Debug - Storage paths:")
        print(f"  - Base path: {self.base_path}")
        print(f"  - Token file: {self.token_file}")
        print(f"  - Credentials file: {self.credentials_file}")

        for directory in directories:
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"✅ Created directory: {directory}")
                except Exception as e:
                    print(f"❌ Failed to create directory {directory}: {e}")
            else:
                print(f"📁 Directory exists: {directory}")

    def _get_user_from_context(self):
        """
        Get current user information from Open WebUI context.
        This is a simplified approach - in production, Open WebUI would provide user context.
        """
        # For now, we'll use a simple approach to identify users
        # In a real Open WebUI integration, this would come from the framework
        return {"user_id": 1, "username": "default_user"}  # Placeholder

    def _save_credentials_to_db(self, creds, user_id=None):
        """Save credentials to database instead of file."""
        if not self.use_database:
            return self._save_credentials_to_file(creds)

        print(f"💾 Saving credentials to database for user {user_id}")

        try:
            import sqlite3

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create table if it doesn't exist (simplified approach)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_google_tokens (
                        user_id INTEGER PRIMARY KEY,
                        access_token TEXT,
                        refresh_token TEXT,
                        token_expiry DATETIME,
                        client_id TEXT,
                        client_secret TEXT,
                        scopes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Insert or update user's tokens
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO user_google_tokens 
                    (user_id, access_token, refresh_token, token_expiry, client_id, client_secret, scopes, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                    (
                        user_id or 1,  # Default to user_id 1 if not provided
                        creds.token,
                        creds.refresh_token,
                        creds.expiry.isoformat() if creds.expiry else None,
                        creds.client_id,
                        creds.client_secret,
                        json.dumps(creds.scopes) if creds.scopes else None,
                    ),
                )

                conn.commit()
                print(f"✅ Credentials saved to database for user {user_id or 1}")

        except Exception as e:
            print(f"❌ Failed to save credentials to database: {e}")
            # Fallback to file storage
            self._save_credentials_to_file(creds)

    def _load_credentials_from_db(self, user_id=None):
        """Load credentials from database instead of file."""
        if not self.use_database:
            return self._load_credentials_from_file()

        print(f"🔍 Loading credentials from database for user {user_id}")

        try:
            import sqlite3

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT access_token, refresh_token, token_expiry, client_id, client_secret, scopes
                    FROM user_google_tokens 
                    WHERE user_id = ?
                """,
                    (user_id or 1,),
                )

                row = cursor.fetchone()
                if not row:
                    print(
                        f"❌ No credentials found in database for user {user_id or 1}"
                    )
                    return None

                (
                    access_token,
                    refresh_token,
                    token_expiry,
                    client_id,
                    client_secret,
                    scopes,
                ) = row

                # Parse expiry
                expiry = None
                if token_expiry:
                    from datetime import datetime

                    expiry = datetime.fromisoformat(token_expiry)

                # Parse scopes
                parsed_scopes = json.loads(scopes) if scopes else self.valves.SCOPES

                # Create credentials
                creds = Credentials(
                    token=access_token,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=parsed_scopes,
                    expiry=expiry,
                )

                print(f"✅ Credentials loaded from database for user {user_id or 1}")
                return creds

        except Exception as e:
            print(f"❌ Failed to load credentials from database: {e}")
            # Fallback to file storage
            return self._load_credentials_from_file()

    def _save_credentials_to_file(self, creds):
        """Fallback method: Save credentials to file."""
        print(f"💾 Saving credentials to file: {self.token_file}")

        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

        try:
            self._ensure_directories()
            with open(self.token_file, "w") as f:
                json.dump(token_data, f, indent=2)
            print(f"✅ Credentials saved successfully to {self.token_file}")
        except Exception as e:
            print(f"❌ Failed to save credentials: {e}")
            raise

    def _load_credentials_from_file(self):
        """Fallback method: Load credentials from file."""
        print(f"🔍 Loading credentials from file: {self.token_file}")
        self._ensure_directories()

        # Check if token file exists
        if not os.path.exists(self.token_file):
            print(f"❌ Token file does not exist: {self.token_file}")
            return None

        try:
            # Load token data
            with open(self.token_file, "r") as f:
                token_data = json.load(f)
            print("✅ Token file loaded successfully")

            # Ensure we have required fields
            required_fields = ["token", "refresh_token", "client_id", "client_secret"]
            if not all(field in token_data for field in required_fields):
                print(
                    f"❌ Missing required token fields. Found: {list(token_data.keys())}"
                )
                return None

            # Create credentials with proper timezone handling
            creds = Credentials(
                token=token_data["token"],
                refresh_token=token_data["refresh_token"],
                token_uri=token_data.get(
                    "token_uri", "https://oauth2.googleapis.com/token"
                ),
                client_id=token_data["client_id"],
                client_secret=token_data["client_secret"],
                scopes=token_data.get("scopes", self.valves.SCOPES),
            )

            # Check if token needs refresh
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed token
                    self._save_credentials_to_file(creds)
                    print("Token refreshed successfully")
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    return None

            return creds

        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None

    def _get_oauth_credentials(self) -> dict:
        """
        Get OAuth client credentials with Railway environment support.
        Prioritizes environment variables over file-based credentials.
        """
        # Priority 1: Environment variables (Railway recommended)
        client_id = os.environ.get("GOOGLE_CLIENT_ID", self.valves.GOOGLE_CLIENT_ID)
        client_secret = os.environ.get(
            "GOOGLE_CLIENT_SECRET", self.valves.GOOGLE_CLIENT_SECRET
        )
        project_id = os.environ.get("GOOGLE_PROJECT_ID", self.valves.GOOGLE_PROJECT_ID)

        if client_id and client_secret:
            return {
                "client_id": client_id,
                "client_secret": client_secret,
                "project_id": project_id or "default",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }

        # Priority 2: File-based credentials
        if not os.path.exists(self.credentials_file):
            # Try to create credentials file from environment if it doesn't exist
            credentials_data = {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "project_id": project_id or "default",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": [self._get_redirect_uri()],
                }
            }

            self._ensure_directories()
            with open(self.credentials_file, "w") as f:
                json.dump(credentials_data, f, indent=2)

            return credentials_data["web"]

        # Priority 3: Load from existing credentials file
        try:
            with open(self.credentials_file, "r") as f:
                credentials = json.load(f)

            # Handle both "installed" and "web" credential formats
            if "installed" in credentials:
                cred_data = credentials["installed"]
            elif "web" in credentials:
                cred_data = credentials["web"]
            else:
                raise ValueError("Invalid credentials format")

            return {
                "client_id": cred_data["client_id"],
                "client_secret": cred_data["client_secret"],
                "project_id": cred_data.get("project_id", "default"),
                "auth_uri": cred_data.get(
                    "auth_uri", "https://accounts.google.com/o/oauth2/auth"
                ),
                "token_uri": cred_data.get(
                    "token_uri", "https://oauth2.googleapis.com/token"
                ),
                "auth_provider_x509_cert_url": cred_data.get(
                    "auth_provider_x509_cert_url",
                    "https://www.googleapis.com/oauth2/v1/certs",
                ),
            }

        except Exception as e:
            raise FileNotFoundError(f"OAuth credentials not found: {str(e)}")

    def _get_api_key(self) -> Optional[str]:
        """
        Get Google API Key for public API access.
        This can improve rate limits and enable some public API features.
        """
        # Priority 1: Environment variable (Railway)
        api_key = os.environ.get("GOOGLE_DRIVE_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY"
        )
        if api_key:
            return api_key

        # Priority 2: Valve configuration
        if self.valves.GOOGLE_API_KEY:
            return self.valves.GOOGLE_API_KEY

        return None

    def _build_service_with_api_key(self, service_name: str, version: str):
        """
        Build a Google API service using API key (for public access only).
        This is useful for operations that don't require user authentication.
        """
        api_key = self._get_api_key()
        if api_key:
            return build(service_name, version, developerKey=api_key)
        else:
            return build(service_name, version)

    class Valves(BaseModel):
        model_config = {"arbitrary_types_allowed": True}

        GOOGLE_CREDENTIALS_FILE: str = Field(
            default="/app/backend/data/opt/oauth_credentials.json",
            description="Path to Google OAuth client credentials JSON file",
        )
        GOOGLE_CLIENT_ID: str = Field(
            default="",
            description="Google OAuth Client ID (Railway environment variable)",
        )
        GOOGLE_CLIENT_SECRET: str = Field(
            default="",
            description="Google OAuth Client Secret (Railway environment variable)",
        )
        GOOGLE_PROJECT_ID: str = Field(
            default="",
            description="Google Cloud Project ID (Railway environment variable)",
        )
        GOOGLE_API_KEY: str = Field(
            default="",
            description="Google API Key for public API access (optional, enhances rate limits)",
        )
        TOKEN_FILE: str = Field(
            default="/app/backend/data/opt/google_token.json",
            description="Path to store Google API token",
        )
        REDIRECT_URI: str = Field(
            default="http://localhost:19328/google-oauth-callback.html",
            description="OAuth redirect URI for authentication flow",
        )
        SCOPES: List[str] = Field(
            default=[
                # Google Drive - Full access
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/drive.metadata",
                "https://www.googleapis.com/auth/drive.metadata.readonly",
                "https://www.googleapis.com/auth/drive.photos.readonly",
                "https://www.googleapis.com/auth/drive.scripts",
                
                # Google Docs
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/documents.readonly",
                
                # Google Sheets
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                
                # Google Slides/Presentations
                "https://www.googleapis.com/auth/presentations",
                "https://www.googleapis.com/auth/presentations.readonly",
                
                # Gmail - Full access
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.labels",
                "https://www.googleapis.com/auth/gmail.insert",
                "https://www.googleapis.com/auth/gmail.metadata",
                "https://www.googleapis.com/auth/gmail.settings.basic",
                "https://www.googleapis.com/auth/gmail.settings.sharing",
                
                # Google Calendar
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.readonly",
                "https://www.googleapis.com/auth/calendar.events",
                "https://www.googleapis.com/auth/calendar.events.readonly",
                "https://www.googleapis.com/auth/calendar.settings.readonly",
                
                # Google Contacts
                "https://www.googleapis.com/auth/contacts",
                "https://www.googleapis.com/auth/contacts.readonly",
                "https://www.googleapis.com/auth/contacts.other.readonly",
                
                # Google Tasks
                "https://www.googleapis.com/auth/tasks",
                "https://www.googleapis.com/auth/tasks.readonly",
                             
                # Google Forms
                "https://www.googleapis.com/auth/forms.body",
                "https://www.googleapis.com/auth/forms.body.readonly",
                "https://www.googleapis.com/auth/forms.responses.readonly",                
            ],
            description="Comprehensive Google API scopes for full Google Workspace access - includes Drive, Gmail, Calendar, Docs, Sheets, Slides, Contacts, Tasks, Keep, Forms, Sites, Apps Script, Classroom, Admin SDK, and more",
        )

    def _get_google_credentials(self):
        """
        Get Google credentials with database-first approach.
        Handles token refresh and timezone issues automatically.
        """
        user_context = self._get_user_from_context()
        user_id = user_context.get("user_id", 1)

        print(f"🔍 Loading credentials for user {user_id}")

        # Try database first, fallback to file
        try:
            creds = self._load_credentials_from_db(user_id)
            if creds:
                # Check if token needs refresh
                if creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        # Save refreshed token
                        self._save_credentials(creds)
                        print("Token refreshed successfully")
                    except Exception as e:
                        print(f"Token refresh failed: {e}")
                        return None
                return creds
        except Exception as e:
            print(f"❌ Database load failed, falling back to file: {e}")

        # Fallback to file-based loading
        return self._load_credentials_from_file()

    def _save_credentials(self, creds):
        """Save credentials using database-first approach."""
        user_context = self._get_user_from_context()
        user_id = user_context.get("user_id", 1)

        print(f"💾 Saving credentials for user {user_id}")

        # Try database first, fallback to file
        try:
            self._save_credentials_to_db(creds, user_id)
        except Exception as e:
            print(f"❌ Database save failed, falling back to file: {e}")
            self._save_credentials_to_file(creds)

    def get_oauth_authorization_url(self) -> str:
        """Generate Google OAuth authorization URL."""
        try:
            credentials = self._get_oauth_credentials()
            client_id = credentials["client_id"]
            redirect_uri = self._get_redirect_uri()

            scope_string = urllib.parse.quote(" ".join(self.valves.SCOPES))
            encoded_redirect = urllib.parse.quote(redirect_uri)

            auth_url = (
                f"https://accounts.google.com/o/oauth2/auth?"
                f"client_id={client_id}&"
                f"redirect_uri={encoded_redirect}&"
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
                f"Copy the message from the callback page and paste it here!"
            )

        except Exception as e:
            return f"❌ Error generating authorization URL: {str(e)}"

    def complete_oauth_setup(self, authorization_code: str) -> str:
        """Complete OAuth setup using authorization code."""
        try:
            credentials = self._get_oauth_credentials()

            token_data = {
                "client_id": credentials["client_id"],
                "client_secret": credentials["client_secret"],
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": self._get_redirect_uri(),
            }

            response = requests.post(
                "https://oauth2.googleapis.com/token", data=token_data, timeout=30
            )
            response.raise_for_status()

            token_info = response.json()

            # Create credentials
            creds = Credentials(
                token=token_info["access_token"],
                refresh_token=token_info.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=credentials["client_id"],
                client_secret=credentials["client_secret"],
                scopes=self.valves.SCOPES,
            )

            # Save credentials
            self._save_credentials(creds)

            return (
                "✅ **OAuth Setup Complete!**\n\n"
                "Google Workspace access has been successfully configured. "
                "You can now use all Google Workspace tools!"
            )

        except Exception as e:
            print(f"🚨 OAuth setup error: {str(e)}")
            return f"❌ Error completing OAuth setup: {str(e)}"

    def authenticate_google_workspace(self) -> str:
        """Check authentication status and provide guidance."""
        # Check for pending OAuth
        pending_result = self._check_pending_oauth()
        if pending_result:
            return pending_result

        try:
            creds = self._get_google_credentials()
            if creds and creds.valid:
                return (
                    "✅ **Google Workspace Authentication Ready**\n\n"
                    "Your Google Workspace is connected and ready to use!"
                )
            elif creds and creds.expired:
                return (
                    "⚠️ **Authentication Expired**\n\n"
                    "Your Google authentication has expired. Let me help you reconnect:\n\n"
                    + self.get_oauth_authorization_url()
                )
            else:
                return (
                    "🔐 **Google Workspace Setup Required**\n\n"
                    "To access Google Drive, Docs, and Sheets, please complete authentication:\n\n"
                    + self.get_oauth_authorization_url()
                )

        except Exception as e:
            return (
                f"❌ **Authentication Error**\n\n"
                f"Error: {str(e)}\n\n"
                f"Let me help you set up fresh authentication:\n\n"
                + self.get_oauth_authorization_url()
            )

    def _check_pending_oauth(self) -> str:
        """Check for pending OAuth authorization from callback."""
        try:
            if os.path.exists(self.pending_oauth_file):
                with open(self.pending_oauth_file, "r") as f:
                    oauth_data = json.load(f)

                code = oauth_data.get("code")
                if code:
                    result = self.complete_oauth_setup(code)
                    os.remove(self.pending_oauth_file)
                    return result
        except Exception:
            pass
        return ""

    # Google Drive Operations
    def list_google_drive_files(
        self, max_results: int = 10, folder_id: Optional[str] = None
    ) -> str:
        """List files in Google Drive."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Not authenticated. Please run authenticate_google_workspace() first."

            service = build("drive", "v3", credentials=creds)

            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"

            results = (
                service.files()
                .list(
                    pageSize=max_results,
                    q=query,
                    orderBy="modifiedTime desc",
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
                )
                .execute()
            )

            items = results.get("files", [])
            if not items:
                return "No files found in Google Drive."

            return json.dumps(items, indent=2)

        except Exception as e:
            return f"❌ Error listing Drive files: {str(e)}"

    def search_google_drive(self, query: str, max_results: int = 10) -> str:
        """Search for files in Google Drive."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Not authenticated. Please run authenticate_google_workspace() first."

            service = build("drive", "v3", credentials=creds)

            # Build search query
            search_query = f"name contains '{query}' or fullText contains '{query}'"
            if "mimeType" in query.lower():
                search_query = query  # Use raw query if it contains mimeType

            results = (
                service.files()
                .list(
                    q=search_query,
                    pageSize=max_results,
                    orderBy="modifiedTime desc",
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
                )
                .execute()
            )

            items = results.get("files", [])
            if not items:
                return f"No files found matching '{query}'."

            return json.dumps(items, indent=2)

        except Exception as e:
            return f"❌ Error searching Google Drive: {str(e)}"

    def create_google_doc(self, title: str, content: str = "") -> str:
        """Create a new Google Document."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Not authenticated. Please run authenticate_google_workspace() first."

            docs_service = build("docs", "v1", credentials=creds)

            # Create document
            doc = docs_service.documents().create(body={"title": title}).execute()
            doc_id = doc["documentId"]

            # Add content if provided
            if content:
                requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
                docs_service.documents().batchUpdate(
                    documentId=doc_id, body={"requests": requests}
                ).execute()

            # Get shareable link
            drive_service = build("drive", "v3", credentials=creds)
            file = (
                drive_service.files().get(fileId=doc_id, fields="webViewLink").execute()
            )

            return json.dumps(
                {
                    "documentId": doc_id,
                    "title": title,
                    "webViewLink": file["webViewLink"],
                },
                indent=2,
            )

        except Exception as e:
            return f"❌ Error creating Google Doc: {str(e)}"

    def create_google_sheet(
        self, title: str, data: Optional[List[List[str]]] = None
    ) -> str:
        """Create a new Google Spreadsheet."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Not authenticated. Please run authenticate_google_workspace() first."

            sheets_service = build("sheets", "v4", credentials=creds)

            # Create spreadsheet
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

            # Get shareable link
            drive_service = build("drive", "v3", credentials=creds)
            file = (
                drive_service.files()
                .get(fileId=spreadsheet_id, fields="webViewLink")
                .execute()
            )

            return json.dumps(
                {
                    "spreadsheetId": spreadsheet_id,
                    "title": title,
                    "webViewLink": file["webViewLink"],
                },
                indent=2,
            )

        except Exception as e:
            return f"❌ Error creating Google Sheet: {str(e)}"

    def get_google_doc_content(self, document_id: str) -> str:
        """Get content from a Google Document."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Not authenticated. Please run authenticate_google_workspace() first."

            docs_service = build("docs", "v1", credentials=creds)
            doc = docs_service.documents().get(documentId=document_id).execute()

            content = []
            for element in doc.get("body", {}).get("content", []):
                if "paragraph" in element:
                    for text_element in element["paragraph"].get("elements", []):
                        if "textRun" in text_element:
                            content.append(text_element["textRun"].get("content", ""))

            return "".join(content)

        except Exception as e:
            return f"❌ Error getting document content: {str(e)}"

    # Alias functions for compatibility with original google_workspace_tools.py
    def create_new_document(self, title: str, content: str = "") -> str:
        """Alias for create_google_doc - for compatibility."""
        return self.create_google_doc(title, content)

    def create_new_spreadsheet(self, title: str, headers: Optional[List[str]] = None, data: Optional[List[List[str]]] = None) -> str:
        """Alias for create_google_sheet - for compatibility."""
        if headers and not data:
            # If only headers provided, use them as first row
            return self.create_google_sheet(title, [headers])
        elif headers and data:
            # If both headers and data provided, combine them
            combined_data = [headers] + data
            return self.create_google_sheet(title, combined_data)
        else:
            # If no headers or only data provided
            return self.create_google_sheet(title, data)

    def read_document_content(self, document_id: str) -> str:
        """Alias for get_google_doc_content - for compatibility."""
        return self.get_google_doc_content(document_id)

    def list_gmail_messages(self, max_results: int = 10) -> str:
        """List recent Gmail messages."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return (
                    "❌ Please authenticate first using authenticate_google_workspace()"
                )

            service = build("gmail", "v1", credentials=creds)

            results = (
                service.users()
                .messages()
                .list(userId="me", maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            if not messages:
                return "📬 No messages found in your Gmail."

            message_list = []
            for msg in messages[:max_results]:
                msg_detail = (
                    service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="metadata")
                    .execute()
                )

                headers = msg_detail["payload"].get("headers", [])
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No Subject",
                )
                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"),
                    "Unknown Sender",
                )

                message_list.append(f"📧 **{subject}**\n   From: {sender}")

            return "📬 **Recent Gmail Messages:**\n\n" + "\n\n".join(message_list)

        except Exception as e:
            return f"❌ Error accessing Gmail: {str(e)}"

    def send_gmail(self, to_email: str, subject: str, body: str) -> str:
        """Send a Gmail message."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return (
                    "❌ Please authenticate first using authenticate_google_workspace()"
                )

            service = build("gmail", "v1", credentials=creds)

            import base64
            from email.mime.text import MIMEText

            msg = MIMEText(body)
            msg["to"] = to_email
            msg["subject"] = subject

            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

            result = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            return (
                f"✅ Email sent successfully to {to_email}!\nMessage ID: {result['id']}"
            )

        except Exception as e:
            return f"❌ Error sending email: {str(e)}"

    def search_gmail(self, query: str, max_results: int = 10) -> str:
        """Search Gmail messages."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return (
                    "❌ Please authenticate first using authenticate_google_workspace()"
                )

            service = build("gmail", "v1", credentials=creds)

            results = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            if not messages:
                return f"🔍 No Gmail messages found for query: '{query}'"

            message_list = []
            for msg in messages[:max_results]:
                msg_detail = (
                    service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="metadata")
                    .execute()
                )

                headers = msg_detail["payload"].get("headers", [])
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No Subject",
                )
                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"),
                    "Unknown Sender",
                )

                message_list.append(f"📧 **{subject}**\n   From: {sender}")

            return f"🔍 **Gmail Search Results for '{query}':**\n\n" + "\n\n".join(
                message_list
            )

        except Exception as e:
            return f"❌ Error searching Gmail: {str(e)}"

    def read_gmail_message(self, message_id: str) -> str:
        """Read the full content of a specific Gmail message."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("gmail", "v1", credentials=creds)
            
            # Get the full message
            message = service.users().messages().get(
                userId="me", id=message_id, format="full"
            ).execute()
            
            # Extract metadata
            headers = message["payload"].get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
            
            # Extract body content
            body = self._extract_message_body(message["payload"])
            
            result = "📧 **Email Details**\n\n"
            result += f"**Subject:** {subject}\n"
            result += f"**From:** {sender}\n"
            result += f"**Date:** {date}\n\n"
            result += f"**Content:**\n{body}"
            
            return result

        except Exception as e:
            return f"❌ Error reading email: {str(e)}"

    def read_gmail_messages_by_sender(self, sender_email: str, max_results: int = 5) -> str:
        """Read recent messages from a specific sender."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("gmail", "v1", credentials=creds)
            
            # Search for messages from the sender
            results = service.users().messages().list(
                userId="me", 
                q=f"from:{sender_email}",
                maxResults=max_results
            ).execute()
            
            messages = results.get("messages", [])
            if not messages:
                return f"📭 No messages found from {sender_email}"

            message_details = []
            for msg in messages:
                # Get full message content
                full_msg = service.users().messages().get(
                    userId="me", id=msg["id"], format="full"
                ).execute()
                
                headers = full_msg["payload"].get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
                
                # Extract body
                body = self._extract_message_body(full_msg["payload"])
                
                message_details.append({
                    "subject": subject,
                    "date": date,
                    "body": body,
                    "id": msg["id"]
                })

            # Format the response
            result = f"📧 **Messages from {sender_email}:**\n\n"
            for i, msg in enumerate(message_details, 1):
                result += f"**{i}. {msg['subject']}**\n"
                result += f"   Date: {msg['date']}\n"
                result += f"   ID: {msg['id']}\n\n"
                result += f"   Content:\n{msg['body']}\n\n"
                result += "---\n\n"
            
            return result

        except Exception as e:
            return f"❌ Error reading messages from {sender_email}: {str(e)}"

    def get_latest_emails_with_content(self, max_results: int = 5) -> str:
        """Get the latest emails with their full content."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("gmail", "v1", credentials=creds)
            
            # Get recent messages
            results = service.users().messages().list(
                userId="me", maxResults=max_results
            ).execute()
            
            messages = results.get("messages", [])
            if not messages:
                return "📬 No messages found in your Gmail."

            message_details = []
            for msg in messages:
                # Get full message content
                full_msg = service.users().messages().get(
                    userId="me", id=msg["id"], format="full"
                ).execute()
                
                headers = full_msg["payload"].get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
                date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
                
                # Extract body
                body = self._extract_message_body(full_msg["payload"])
                
                message_details.append({
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "body": body,
                    "id": msg["id"]
                })

            # Format the response
            result = f"📧 **Latest {len(message_details)} emails with content:**\n\n"
            for i, msg in enumerate(message_details, 1):
                result += f"**{i}. {msg['subject']}**\n"
                result += f"   From: {msg['sender']}\n"
                result += f"   Date: {msg['date']}\n"
                result += f"   ID: {msg['id']}\n\n"
                result += f"   Content:\n{msg['body']}\n\n"
                result += "---\n\n"
            
            return result

        except Exception as e:
            return f"❌ Error getting latest emails: {str(e)}"

    def _extract_message_body(self, payload) -> str:
        """Extract the body text from a Gmail message payload."""
        body = ""
        
        if "parts" in payload:
            # Multi-part message
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        import base64
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        break
                elif part["mimeType"] == "text/html" and not body:
                    if "data" in part["body"]:
                        import base64
                        html_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        # Simple HTML to text conversion
                        import re
                        body = re.sub(r'<[^>]+>', '', html_body)
        else:
            # Single part message
            if payload["mimeType"] == "text/plain":
                if "data" in payload["body"]:
                    import base64
                    body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
            elif payload["mimeType"] == "text/html":
                if "data" in payload["body"]:
                    import base64
                    html_body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
                    # Simple HTML to text conversion
                    import re
                    body = re.sub(r'<[^>]+>', '', html_body)
        
        return body.strip() if body else "No readable content found"

    def read_emails_from_wes_mcdowell(self) -> str:
        """Read the content of emails from Wes McDowell - specific function for the user's request."""
        return self.read_gmail_messages_by_sender("wes@wesmcdowell.com", 5)

    def read_todays_emails_with_content(self) -> str:
        """Get today's emails with their full content."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "🔐 **Authentication Required**\n\nPlease call authenticate_google_workspace() first to set up Google access, then I can read your emails."

            service = build("gmail", "v1", credentials=creds)
            
            # Get today's date for search
            import datetime
            today = datetime.date.today()
            today_str = today.strftime("%Y/%m/%d")
            
            # Search for emails from today
            results = service.users().messages().list(
                userId="me", 
                q=f"after:{today_str}",
                maxResults=10
            ).execute()
            
            messages = results.get("messages", [])
            
            if not messages:
                return f"📭 **No new emails today** ({today.strftime('%B %d, %Y')})\n\nYour inbox is clear for today!"

            message_details = []
            for msg in messages:
                # Get full message content
                full_msg = service.users().messages().get(
                    userId="me", id=msg["id"], format="full"
                ).execute()
                
                headers = full_msg["payload"].get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
                date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
                
                # Extract body
                body = self._extract_message_body(full_msg["payload"])
                
                message_details.append({
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "body": body,
                    "id": msg["id"]
                })

            # Format the response
            total_count = len(message_details)
            result = f"📬 **{total_count} emails from today ({today.strftime('%B %d, %Y')}) with content:**\n\n"
            
            for i, msg in enumerate(message_details, 1):
                result += f"**{i}. {msg['subject']}**\n"
                result += f"   From: {msg['sender']}\n"
                result += f"   Date: {msg['date']}\n\n"
                result += f"   **Content:**\n{msg['body'][:500]}{'...' if len(msg['body']) > 500 else ''}\n\n"
                result += "---\n\n"
            
            return result

        except Exception as e:
            return f"❌ Error reading today's emails: {str(e)}"

    def list_calendar_events(self, max_results: int = 10) -> str:
        """List upcoming Calendar events."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return (
                    "❌ Please authenticate first using authenticate_google_workspace()"
                )

            service = build("calendar", "v3", credentials=creds)

            import datetime

            now = datetime.datetime.utcnow().isoformat() + "Z"

            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            if not events:
                return "📅 No upcoming events found in your calendar."

            event_list = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                summary = event.get("summary", "No Title")
                event_list.append(f"📅 **{summary}**\n   📍 {start}")

            return "📅 **Upcoming Calendar Events:**\n\n" + "\n\n".join(event_list)

        except Exception as e:
            return f"❌ Error accessing Calendar: {str(e)}"

    def create_calendar_event(
        self, title: str, start_time: str, end_time: str, description: str = ""
    ) -> str:
        """Create a Calendar event."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return (
                    "❌ Please authenticate first using authenticate_google_workspace()"
                )

            service = build("calendar", "v3", credentials=creds)

            event = {
                "summary": title,
                "description": description,
                "start": {
                    "dateTime": start_time,
                    "timeZone": "America/Chicago",
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": "America/Chicago",
                },
            }

            event = service.events().insert(calendarId="primary", body=event).execute()

            return f"✅ Calendar event created successfully!\n📅 **{title}**\nEvent ID: {event['id']}"

        except Exception as e:
            return f"❌ Error creating calendar event: {str(e)}"

    # Google Contacts Functions
    def list_contacts(self, max_results: int = 20) -> str:
        """List Google Contacts."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("people", "v1", credentials=creds)
            
            results = service.people().connections().list(
                resourceName='people/me',
                personFields='names,emailAddresses,phoneNumbers,organizations',
                pageSize=max_results
            ).execute()
            
            connections = results.get('connections', [])
            if not connections:
                return "📇 No contacts found in your Google Contacts."

            contact_list = []
            for person in connections:
                names = person.get('names', [])
                emails = person.get('emailAddresses', [])
                phones = person.get('phoneNumbers', [])
                
                name = names[0].get('displayName', 'No Name') if names else 'No Name'
                email = emails[0].get('value', 'No Email') if emails else 'No Email'
                phone = phones[0].get('value', 'No Phone') if phones else 'No Phone'
                
                contact_list.append(f"👤 **{name}**\n   📧 {email}\n   📞 {phone}")

            return f"📇 **Your Google Contacts ({len(contact_list)} contacts):**\n\n" + "\n\n".join(contact_list)

        except Exception as e:
            return f"❌ Error accessing contacts: {str(e)}"

    def search_contacts(self, query: str) -> str:
        """Search Google Contacts."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("people", "v1", credentials=creds)
            
            results = service.people().searchContacts(
                query=query,
                readMask='names,emailAddresses,phoneNumbers'
            ).execute()
            
            contacts = results.get('results', [])
            if not contacts:
                return f"🔍 No contacts found matching '{query}'"

            contact_list = []
            for result in contacts:
                person = result.get('person', {})
                names = person.get('names', [])
                emails = person.get('emailAddresses', [])
                phones = person.get('phoneNumbers', [])
                
                name = names[0].get('displayName', 'No Name') if names else 'No Name'
                email = emails[0].get('value', 'No Email') if emails else 'No Email'
                phone = phones[0].get('value', 'No Phone') if phones else 'No Phone'
                
                contact_list.append(f"👤 **{name}**\n   📧 {email}\n   📞 {phone}")

            return f"🔍 **Contacts matching '{query}' ({len(contact_list)} found):**\n\n" + "\n\n".join(contact_list)

        except Exception as e:
            return f"❌ Error searching contacts: {str(e)}"

    # Google Tasks Functions
    def list_tasks(self, tasklist: str = '@default') -> str:
        """List Google Tasks."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("tasks", "v1", credentials=creds)
            
            results = service.tasks().list(tasklist=tasklist).execute()
            items = results.get('items', [])
            
            if not items:
                return "✅ No tasks found in your Google Tasks."

            task_list = []
            for item in items:
                title = item.get('title', 'No Title')
                status = item.get('status', 'needsAction')
                due = item.get('due', 'No due date')
                notes = item.get('notes', '')
                
                status_icon = "✅" if status == "completed" else "📋"
                task_info = f"{status_icon} **{title}**"
                if due != 'No due date':
                    task_info += f"\n   📅 Due: {due[:10]}"
                if notes:
                    task_info += f"\n   📝 Notes: {notes[:100]}{'...' if len(notes) > 100 else ''}"
                
                task_list.append(task_info)

            return f"📋 **Your Google Tasks ({len(task_list)} tasks):**\n\n" + "\n\n".join(task_list)

        except Exception as e:
            return f"❌ Error accessing tasks: {str(e)}"

    def create_task(self, title: str, notes: str = "", due_date: str = "") -> str:
        """Create a new Google Task."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("tasks", "v1", credentials=creds)
            
            task = {
                'title': title,
                'notes': notes,
            }
            
            if due_date:
                task['due'] = due_date

            result = service.tasks().insert(tasklist='@default', body=task).execute()
            
            return f"✅ Task created successfully!\n📋 **{title}**\nTask ID: {result['id']}"

        except Exception as e:
            return f"❌ Error creating task: {str(e)}"

    # Google Forms Functions
    def list_forms(self) -> str:
        """List Google Forms."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            # Note: Google Forms API has limited listing capabilities
            # This is a basic implementation
            return "📋 **Google Forms Integration**\n\nNote: Google Forms API has limited direct listing capabilities. Use the Google Drive integration to find your forms, or create new forms using create_google_form()."

        except Exception as e:
            return f"❌ Error accessing forms: {str(e)}"

    def create_google_form(self, title: str, description: str = "") -> str:
        """Create a new Google Form."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("forms", "v1", credentials=creds)
            
            form = {
                "info": {
                    "title": title,
                    "description": description
                }
            }

            result = service.forms().create(body=form).execute()
            
            form_id = result['formId']
            form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
            
            return f"✅ Google Form created successfully!\n📋 **{title}**\nForm ID: {form_id}\nEdit URL: {form_url}"

        except Exception as e:
            return f"❌ Error creating form: {str(e)}"

    # Google Sites Functions  
    def list_sites(self) -> str:
        """List Google Sites."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("sites", "v1", credentials=creds)
            
            results = service.sites().list().execute()
            sites = results.get('sites', [])
            
            if not sites:
                return "🌐 No Google Sites found in your account."

            site_list = []
            for site in sites:
                name = site.get('name', 'Unnamed Site')
                site_url = site.get('siteUrl', 'No URL')
                title = site.get('title', 'No Title')
                
                site_list.append(f"🌐 **{title}**\n   Name: {name}\n   URL: {site_url}")

            return f"🌐 **Your Google Sites ({len(site_list)} sites):**\n\n" + "\n\n".join(site_list)

        except Exception as e:
            return f"❌ Error accessing sites: {str(e)}"

    # User Info Functions
    def get_user_info(self) -> str:
        """Get authenticated user's profile information."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Please authenticate first using authenticate_google_workspace()"

            service = build("oauth2", "v2", credentials=creds)
            
            user_info = service.userinfo().get().execute()
            
            name = user_info.get('name', 'No Name')
            email = user_info.get('email', 'No Email')
            picture = user_info.get('picture', 'No Picture')
            verified_email = user_info.get('verified_email', False)
            
            result = "👤 **User Profile Information**\n\n"
            result += f"**Name:** {name}\n"
            result += f"**Email:** {email}\n"
            result += f"**Email Verified:** {'✅ Yes' if verified_email else '❌ No'}\n"
            result += f"**Profile Picture:** {picture}\n"
            
            return result

        except Exception as e:
            return f"❌ Error getting user info: {str(e)}"

    # Natural Language Interface
    def handle_user_message(self, message: str) -> str:
        """Process natural language requests for Google Workspace operations."""
        message_lower = message.lower().strip()

        # OAuth completion
        oauth_result = self._process_oauth_message(message)
        if oauth_result:
            return oauth_result

        # Drive operations
        if any(word in message_lower for word in ["drive", "files", "documents"]):
            if "proposal" in message_lower:
                return self._handle_proposal_search(message)
            elif "show" in message_lower or "list" in message_lower:
                return self.show_my_drive_files()
            elif "search" in message_lower:
                query = re.sub(r".*search.*for\s+", "", message_lower)
                return self.search_my_drive(query)

        # Handle natural language search
        if any(word in message_lower for word in ["find", "show", "search"]):
            return self._handle_natural_language_search(message)

        return ""

    def _process_oauth_message(self, message: str) -> str:
        """Process OAuth completion messages."""
        patterns = [
            r"Complete authentication with code:\s*([0-9A-Za-z\-_/]+)",
            r"Authorization code:\s*([0-9A-Za-z\-_/]+)",
            r"Code:\s*([0-9A-Za-z\-_/]+)",
            r"4/[0-9A-Za-z\-_]+",
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                auth_code = match.group(1) if match.lastindex else match.group(0)
                auth_code = re.sub(r"[^\w\-_/]", "", auth_code)

                if len(auth_code) > 10:
                    return self.complete_oauth_setup(auth_code)

        return ""

    def _handle_proposal_search(self, message: str) -> str:
        """Handle search for proposal documents."""
        try:
            # Search for Google Docs with "Proposal" in name
            results = self.search_google_drive("Proposal", max_results=10)
            files = json.loads(results)

            # Filter for Google Docs
            docs = [f for f in files if "document" in f.get("mimeType", "")]
            docs = docs[:3]  # Take top 3

            if not docs:
                return "❌ No Google Docs with 'Proposal' found in your Drive."

            response = "📄 **Newest 3 Google Docs with 'Proposal' in the name:**\n\n"
            for i, doc in enumerate(docs, 1):
                name = doc.get("name", "Unknown")
                modified = doc.get("modifiedTime", "Unknown")[:10]
                link = doc.get("webViewLink", "")

                response += f"{i}. **{name}**\n"
                response += f"   Last modified: {modified}\n"
                if link:
                    response += f"   [Open Document]({link})\n"
                response += "\n"

            return response

        except Exception as e:
            return f"❌ Error searching for proposals: {str(e)}"

    def _handle_natural_language_search(self, message: str) -> str:
        """Handle natural language search requests with flexible query extraction."""
        message_lower = message.lower().strip()

        # Extract search query and file type from natural language
        search_patterns = [
            (r"find.*(?:google docs?|documents?)\s+(?:with\s+)?(.+)", "document"),
            (
                r"find.*(?:google sheets?|spreadsheets?)\s+(?:with\s+)?(.+)",
                "spreadsheet",
            ),
            (
                r"find.*(?:google slides?|presentations?)\s+(?:with\s+)?(.+)",
                "presentation",
            ),
            (r"find.*(?:pdf|pdfs)\s+(?:with\s+)?(.+)", "pdf"),
            (r"find.*(?:files?|docs?)\s+(?:with\s+)?(.+)", None),
            (r"search.*(?:for\s+)?(.+)", None),
            (r"show.*(?:me\s+)?(.+)", None),
        ]

        query = None
        file_type = None
        max_results = 10

        # Try to extract number
        num_match = re.search(r"(\d+)\s*(?:newest|latest|recent|top)?", message_lower)
        if num_match:
            max_results = int(num_match.group(1))

        # Try to extract query and file type
        for pattern, mime_filter in search_patterns:
            match = re.search(pattern, message_lower)
            if match:
                query = match.group(1).strip()
                file_type = mime_filter
                break

        # Default to simple keyword extraction if no pattern matched
        if not query:
            # Remove common words and extract the main search term
            words = message_lower.split()
            keywords = [
                w
                for w in words
                if w
                not in [
                    "find",
                    "show",
                    "me",
                    "my",
                    "the",
                    "search",
                    "for",
                    "in",
                    "drive",
                    "google",
                    "docs",
                    "files",
                    "documents",
                ]
            ]
            query = " ".join(keywords) if keywords else "*"

        # Build search query
        search_query = query
        if file_type:
            mime_map = {
                "document": "application/vnd.google-apps.document",
                "spreadsheet": "application/vnd.google-apps.spreadsheet",
                "presentation": "application/vnd.google-apps.presentation",
                "pdf": "application/pdf",
            }
            if file_type in mime_map:
                search_query = f"mimeType='{mime_map[file_type]}' and (name contains '{query}' or fullText contains '{query}')"
            else:
                search_query = f"name contains '{query}' or fullText contains '{query}'"

        return self.search_my_drive(
            query=search_query, max_results=max_results, file_type_hint=file_type
        )

    def search_my_drive(
        self, query: str, max_results: int = 10, file_type_hint: Optional[str] = None
    ) -> str:
        """Flexible search with user-friendly formatting."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "❌ Not authenticated. Please run authenticate_google_workspace() first."

            service = build("drive", "v3", credentials=creds)

            # Use provided query or build from hint
            search_query = query
            if file_type_hint and "mimeType" not in query.lower():
                mime_map = {
                    "document": "application/vnd.google-apps.document",
                    "spreadsheet": "application/vnd.google-apps.spreadsheet",
                    "presentation": "application/vnd.google-apps.presentation",
                    "pdf": "application/pdf",
                }
                if file_type_hint in mime_map:
                    search_query = f"mimeType='{mime_map[file_type_hint]}' and (name contains '{query}' or fullText contains '{query}')"

            results = (
                service.files()
                .list(
                    q=search_query,
                    pageSize=max_results,
                    orderBy="modifiedTime desc",
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
                )
                .execute()
            )

            items = results.get("files", [])
            if not items:
                return f"🔍 No files found matching '{query}'."

            # Format results nicely
            response = (
                f"🔍 **Search Results** ({len(items)} files found for '{query}'):\n\n"
            )

            for i, file in enumerate(items, 1):
                name = file.get("name", "Unknown")
                mime_type = file.get("mimeType", "Unknown")

                # Convert mime types to friendly names
                type_map = {
                    "application/vnd.google-apps.document": "📄 Google Doc",
                    "application/vnd.google-apps.spreadsheet": "📊 Google Sheet",
                    "application/vnd.google-apps.presentation": "🎯 Google Slides",
                    "application/pdf": "📑 PDF",
                    "application/vnd.google-apps.folder": "📁 Folder",
                }

                file_type = type_map.get(mime_type, f"📄 {mime_type.split('.')[-1]}")
                modified = file.get("modifiedTime", "Unknown")[:10]
                link = file.get("webViewLink", "")

                response += f"{i}. **{name}**\n"
                response += f"   Type: {file_type}\n"
                response += f"   Modified: {modified}\n"
                if link:
                    response += f"   [Open File]({link})\n"
                response += "\n"

            return response

        except Exception as e:
            return f"❌ Error searching Google Drive: {str(e)}"

    # User-friendly wrappers
    def show_my_drive_files(self, max_results: int = 10) -> str:
        """Show user's Google Drive files in a friendly format."""
        result = self.list_google_drive_files(max_results)
        try:
            files = json.loads(result)
            if not files:
                return "📁 Your Google Drive is empty or no files found."

            response = f"📁 **Your Google Drive Files** ({len(files)} files):\n\n"
            for i, file in enumerate(files, 1):
                name = file.get("name", "Unknown")
                mime_type = file.get("mimeType", "Unknown").split(".")[-1]
                modified = file.get("modifiedTime", "Unknown")[:10]

                response += f"{i}. **{name}** ({mime_type})\n"
                response += f"   Modified: {modified}\n\n"

            return response
        except Exception:
            return result

    def quick_start_google_workspace(self) -> str:
        """One-click start for Google Workspace setup."""
        return self.authenticate_google_workspace()

    def help_me_setup_google_workspace(self) -> str:
        """Comprehensive setup guide."""
        return (
            "🚀 **Google Workspace Setup Guide**\n\n"
            "**For Railway Deployment:**\n"
            "1. Set these Railway environment variables:\n"
            "   • GOOGLE_CLIENT_ID\n"
            "   • GOOGLE_CLIENT_SECRET\n"
            "   • GOOGLE_PROJECT_ID (optional)\n\n"
            "**Quick Setup:**\n"
            "1. Call authenticate_google_workspace()\n"
            "2. Follow the authorization link\n"
            "3. Complete authentication\n\n"
            "**🎯 Full Google Workspace Access - 40+ Functions Available:**\n\n"
            "📁 **Drive (7 functions):**\n"
            "• show_my_drive_files() - View your files\n"
            "• search_my_drive('keyword') - Search files\n"
            "• search_google_drive('query') - Advanced search\n"
            "• create_google_doc('Title', 'content') - Create docs\n"
            "• create_google_sheet('Title', data) - Create sheets\n"
            "• get_google_doc_content('doc_id') - Read document\n"
            "• list_google_drive_files() - List all files\n\n"
            "📧 **Gmail (9 functions):**\n"
            "• list_gmail_messages() - Get recent emails\n"
            "• send_gmail('to', 'subject', 'body') - Send email\n"
            "• search_gmail('query') - Search emails\n"
            "• read_gmail_message('id') - Read email content\n"
            "• read_gmail_messages_by_sender('email') - Emails from sender\n"
            "• get_latest_emails_with_content() - Recent emails with content\n"
            "• check_my_email_today() - Today's emails\n"
            "• read_todays_emails_with_content() - Today's emails with content\n"
            "• read_emails_from_wes_mcdowell() - Specific sender example\n\n"
            "📅 **Calendar (2 functions):**\n"
            "• list_calendar_events() - Get upcoming events\n"
            "• create_calendar_event('title', 'start', 'end') - Create event\n\n"
            "📇 **Contacts (2 functions):**\n"
            "• list_contacts() - View your contacts\n"
            "• search_contacts('query') - Search contacts\n\n"
            "📋 **Tasks (2 functions):**\n"
            "• list_tasks() - View your tasks\n"
            "• create_task('title', 'notes', 'due_date') - Create task\n\n"
            "📝 **Forms (2 functions):**\n"
            "• list_forms() - View your forms\n"
            "• create_google_form('title', 'description') - Create form\n\n"
            "🌐 **Sites (1 function):**\n"
            "• list_sites() - View your Google Sites\n\n"
            "👤 **User Info (1 function):**\n"
            "• get_user_info() - Get your profile information\n\n"
            "🔗 **Aliases (3 functions):**\n"
            "• create_new_document() - Alias for create_google_doc\n"
            "• create_new_spreadsheet() - Alias for create_google_sheet\n"
            "• read_document_content() - Alias for get_google_doc_content\n\n"
            "✨ **With comprehensive Google API scopes covering Drive, Gmail, Calendar, Contacts, Tasks, Forms, Sites, Admin SDK, Classroom, and more!**"
        )

    def what_google_workspace_tools_do_i_have(self) -> str:
        """List all available Google Workspace functions for the AI assistant."""
        return (
            "🤖 **AI Assistant: You have these Google Workspace tools available:**\n\n"
            "📁 **Google Drive (7 functions):**\n"
            "• show_my_drive_files(max_results=10)\n"
            "• search_my_drive(query, max_results=10)\n"
            "• search_google_drive(query, max_results=10)\n"
            "• list_google_drive_files(max_results=10)\n"
            "• create_google_doc(title, content='')\n"
            "• create_google_sheet(title, data=[])\n"
            "• get_google_doc_content(document_id)\n\n"
            "📧 **Gmail (9 functions):**\n"
            "• list_gmail_messages(max_results=10)\n"
            "• send_gmail(to_email, subject, body)\n"
            "• search_gmail(query, max_results=10)\n"
            "• read_gmail_message(message_id)\n"
            "• read_gmail_messages_by_sender(sender_email, max_results=5)\n"
            "• get_latest_emails_with_content(max_results=5)\n"
            "• check_my_email_today()\n"
            "• read_todays_emails_with_content()\n"
            "• read_emails_from_wes_mcdowell()\n\n"
            "📅 **Calendar (2 functions):**\n"
            "• list_calendar_events(max_results=10)\n"
            "• create_calendar_event(title, start_time, end_time, description='')\n\n"
            "📇 **Contacts (2 functions):**\n"
            "• list_contacts(max_results=20)\n"
            "• search_contacts(query)\n\n"
            "� **Tasks (2 functions):**\n"
            "• list_tasks(tasklist='@default')\n"
            "• create_task(title, notes='', due_date='')\n\n"
            "📝 **Forms (2 functions):**\n"
            "• list_forms()\n"
            "• create_google_form(title, description='')\n\n"
            "🌐 **Sites (1 function):**\n"
            "• list_sites()\n\n"
            "👤 **User Info (1 function):**\n"
            "• get_user_info()\n\n"
            "🔗 **Aliases (3 functions):**\n"
            "• create_new_document(title, content='')\n"
            "• create_new_spreadsheet(title, headers=[], data=[])\n"
            "• read_document_content(document_id)\n\n"
            "�🔧 **Setup & Auth (7 functions):**\n"
            "• authenticate_google_workspace()\n"
            "• get_oauth_authorization_url()\n"
            "• complete_oauth_setup(authorization_code)\n"
            "• help_me_setup_google_workspace()\n"
            "• what_google_workspace_tools_do_i_have()\n"
            "• ai_please_execute_not_show_code()\n"
            "• quick_start_google_workspace()\n\n"
            "⚡ **TOTAL: 40+ functions covering ALL Google Workspace services!**\n"
            "🔥 **You can use ANY of these functions to help users with Google Workspace tasks!**"
        )

    def ai_assistant_execute_gmail_check(self) -> str:
        """AI Assistant: Execute this function to check user's Gmail messages - don't show code."""
        try:
            # First check if authenticated
            creds = self._get_google_credentials()
            if not creds:
                return "🔐 **Authentication Required First**\n\nPlease call authenticate_google_workspace() first to set up Google access."
            
            # If authenticated, get recent messages
            return self.list_gmail_messages(10)
            
        except Exception as e:
            return f"❌ Error checking Gmail: {str(e)}"

    def check_my_email_today(self) -> str:
        """Check if user received any new emails today."""
        try:
            creds = self._get_google_credentials()
            if not creds:
                return "🔐 **Authentication Required**\n\nPlease call authenticate_google_workspace() first to set up Google access, then I can check your emails."

            service = build("gmail", "v1", credentials=creds)
            
            # Get today's date for search
            import datetime
            today = datetime.date.today()
            today_str = today.strftime("%Y/%m/%d")
            
            # Search for emails from today
            results = service.users().messages().list(
                userId="me", 
                q=f"after:{today_str}",
                maxResults=20
            ).execute()
            
            messages = results.get("messages", [])
            
            if not messages:
                return f"📭 **No new emails today** ({today.strftime('%B %d, %Y')})\n\nYour inbox is clear for today!"

            # Get details for today's messages
            message_list = []
            for msg in messages[:10]:  # Limit to 10 most recent
                msg_detail = service.users().messages().get(
                    userId="me", id=msg["id"], format="metadata"
                ).execute()
                
                headers = msg_detail["payload"].get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
                date_header = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
                
                message_list.append(f"📧 **{subject}**\n   From: {sender}\n   Date: {date_header}")

            total_count = len(messages)
            showing_count = min(10, total_count)
            
            result = f"📬 **You received {total_count} new email(s) today** ({today.strftime('%B %d, %Y')})\n\n"
            result += f"**Showing {showing_count} most recent:**\n\n"
            result += "\n\n".join(message_list)
            
            if total_count > 10:
                result += f"\n\n📋 *({total_count - 10} more emails not shown)*"
                
            return result

        except Exception as e:
            return f"❌ Error checking today's emails: {str(e)}"

    def ai_please_execute_not_show_code(self) -> str:
        """Reminder for AI: Execute functions, don't show code snippets."""
        return (
            "🤖 **AI Assistant Instructions:**\n\n"
            "❌ **DON'T DO THIS:**\n"
            "```python\n"
            "what_google_workspace_tools_do_i_have()\n"
            "```\n\n"
            "✅ **DO THIS INSTEAD:**\n"
            "Actually CALL/EXECUTE the function directly!\n\n"
            "**Available executable functions:**\n"
            "• Call authenticate_google_workspace() to start setup\n"
            "• Call list_gmail_messages() to check emails\n"
            "• Call show_my_drive_files() to see Drive files\n"
            "• Call what_google_workspace_tools_do_i_have() to see all tools\n\n"
            "🔥 **EXECUTE THE FUNCTIONS - DON'T SHOW CODE!**"
        )
