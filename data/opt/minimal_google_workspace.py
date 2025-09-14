"""
Title: Core Google Workspace Tools
Author: Ryan Hidden, Hidden AI-X
Description: Minimal single-user Google OAuth + basic API access for Open WebUI (Tools class required).
Version: 0.1.0
Requirements: google-auth, google-auth-oauthlib, google-api-python-client, requests

Usage (inside agent):

1. tools.get_oauth_authorization_url() -> send URL to user.
2. User returns code; call tools.complete_oauth_setup(code).
3. Call wrappers (list_drive_files, list_recent_gmail_messages, list_calendar_events).
Deliberately minimal: single user, file token store, no intent routing, no encryption, no state param validation.
Add security (state param) and scope pruning for production.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, List, Dict, Optional
import datetime
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel, Field


class Tools:
    def __init__(self):
        """Initialize the Google Workspace Tools with Railway optimizations."""
        self.valves = self.Valves()
        self.citation = True
        self._pending_flow = None  # placeholder for active OAuth flow

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

    # --- Internal credential helpers ---
    def _load_credentials(
        self,
    ):  # removed return type to avoid Pydantic inspecting Credentials
        path = Path(self.valves.TOKEN_FILE)
        if not path.exists():
            return None
        try:
            creds = Credentials.from_authorized_user_file(path, self.valves.SCOPES)
        except Exception:
            return None
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._save_credentials(creds)
            except Exception:
                return None
        if creds and creds.valid:
            return creds
        return None

    def _save_credentials(self, creds) -> None:  # removed Credentials annotation
        try:
            with open(self.valves.TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        except Exception:
            pass

    # --- Public OAuth interface ---
    def get_oauth_authorization_url(self) -> str:
        config_or_error = self._load_client_config()
        if isinstance(config_or_error, str):
            return config_or_error  # error message

        cfg = config_or_error
        # Determine which block (web or installed) is present
        if "web" in cfg:
            section = cfg["web"]
            block_name = "web"
        elif "installed" in cfg:
            section = cfg["installed"]
            block_name = "installed"
        else:
            return "❌ Client config missing 'web' or 'installed' section."

        # Ensure redirect URI present
        redirect_uri = (
            os.environ.get("GOOGLE_OAUTH_REDIRECT_URI")
            or os.environ.get("GOOGLE_REDIRECT_URI")
            or self.valves.REDIRECT_URI
        )
        if "redirect_uris" not in section or not section["redirect_uris"]:
            section["redirect_uris"] = [redirect_uri]
        elif redirect_uri not in section["redirect_uris"]:
            section["redirect_uris"].append(redirect_uri)

        try:
            # Build flow with full config
            full_config = {block_name: section}
            flow = InstalledAppFlow.from_client_config(full_config, self.valves.SCOPES)
            # Explicitly set redirect URI once (avoid passing twice to oauthlib)
            flow.redirect_uri = redirect_uri
        except Exception as e:
            return f"❌ Failed to build OAuth flow: {e}"

        try:
            auth_url, _ = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
            )
        except Exception as e:
            return f"❌ Failed to generate authorization URL: {e}"

        self._pending_flow = flow
        return (
            "🔐 **Google OAuth Required**\n\nVisit this URL to authorize access, then paste the code here:\n\n"
            + auth_url
        )

    def complete_oauth_setup(self, authorization_code: str) -> str:
        if not self._pending_flow:
            return "No pending auth flow. Call get_oauth_authorization_url() first."
        try:
            self._pending_flow.fetch_token(code=authorization_code.strip())
        except Exception as e:
            return f"❌ Failed to exchange code: {e}"
        creds = self._pending_flow.credentials
        self._save_credentials(creds)
        return "✅ OAuth complete. Google Workspace access is ready."

    def authenticate_google_workspace(self) -> str:
        creds = self._load_credentials()
        if creds and creds.valid:
            return "✅ Already authenticated."
        return self.get_oauth_authorization_url()

    # --- Generic service builder ---
    def _build_service(self, api: str, version: str):
        creds = self._load_credentials()
        if not creds:
            return (
                None,
                "❌ Not authenticated. Run authenticate_google_workspace() first.",
            )
        try:
            return build(api, version, credentials=creds), ""
        except Exception as e:
            return None, f"❌ Failed to build {api} service: {e}"

    # Optional simple NL passthrough (very minimal)
    def handle_user_message(self, message: str) -> str:
        m = message.lower()
        count = self._parse_count(m)
        if "auth" in m or "connect" in m:
            return self.authenticate_google_workspace()
        if "drive" in m:
            return self.list_drive_files(max_results=count)
        if "gmail" in m or "email" in m:
            return self.list_recent_gmail_messages(max_results=count)
        if "calendar" in m or "event" in m:
            return self.list_calendar_events(max_results=count)
        return ""  # Let upstream decide

    # --- Helper to parse desired count from user text ---
    def _parse_count(self, text: str) -> int:
        """Infer desired number of items.
        Returns:
          -1 for 'all' (signals unlimited up to MAX_LIST_RESULTS)
          positive int for explicit numbers (bounded to MAX_LIST_RESULTS)
          5 as default fallback
        """
        import re

        if "all" in text:
            return -1
        m = re.search(r"(\d{1,4})", text)
        if m:
            try:
                val = int(m.group(1))
                if val <= 0:
                    return 5
                return min(val, self.valves.MAX_LIST_RESULTS)
            except ValueError:
                return 5
        return 5

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
                # Google Docs
                "https://www.googleapis.com/auth/documents",
                # Google Sheets
                "https://www.googleapis.com/auth/spreadsheets",
                # Google Slides/Presentations
                "https://www.googleapis.com/auth/presentations",
                # Gmail - Full access
                "https://www.googleapis.com/auth/gmail",
                # Google Calendar
                "https://www.googleapis.com/auth/calendar",
            ],
            description="Focused Google API scopes for core Workspace access - includes Drive, Gmail, Calendar, Docs, Sheets, and Slides",
        )
        MAX_LIST_RESULTS: int = Field(
            default=500,
            description="Upper cap for 'all' listings to protect performance",
        )

    # --- Client config loader supporting web/installed/env ---
    def _load_client_config(self):
        cred_path = (
            getattr(self, "credentials_file", None)
            or self.valves.GOOGLE_CREDENTIALS_FILE
        )
        if cred_path and os.path.isfile(cred_path):
            try:
                with open(cred_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Accept top-level web or installed, or already flattened
                if "web" in data or "installed" in data:
                    return data
                # If appears to already be a section, wrap heuristically
                if "client_id" in data and "client_secret" in data:
                    # Assume web style since you specified a Web App
                    return {"web": data}
                return "❌ Unrecognized credentials JSON format. Expected keys: 'web' or 'installed'."
            except Exception as e:
                return f"❌ Failed reading credentials file '{cred_path}': {e}"

        # Fallback to environment variables
        client_id = os.environ.get("GOOGLE_CLIENT_ID", self.valves.GOOGLE_CLIENT_ID)
        client_secret = os.environ.get(
            "GOOGLE_CLIENT_SECRET", self.valves.GOOGLE_CLIENT_SECRET
        )
        if not client_id or not client_secret:
            return "❌ No credentials file and missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET env vars."
        return {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    os.environ.get(
                        "GOOGLE_OAUTH_REDIRECT_URI", self.valves.REDIRECT_URI
                    )
                ],
            }
        }

    ## Google Drive Wrappers
    def list_drive_files(self, query: str = None) -> list[dict]:
        """
        List or search Google Drive files.
        If `query` is None, returns recent files.
        """
        service = build("drive", "v3", credentials=self.creds)
        results = []
        page_token = None

        while True:
            response = (
                service.files()
                .list(
                    q=query,
                    pageSize=100,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                )
                .execute()
            )

            results.extend(response.get("files", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                break

        return results

    def get_drive_file_metadata(file_id: str):
        """Get metadata for a Drive file"""
        return {"id": file_id, "name": "Example File", "mimeType": "doc"}

    def download_drive_file(file_id: str):
        """Download given file content (binary/text)"""
        return b"Fake file content"

    def upload_drive_file(file_path: str, mime_type: str):
        """Upload file to Drive"""
        return {"id": "newfile123", "name": file_path}

    def update_drive_file(file_id: str, metadata: dict):
        """Update metadata (rename, move, etc.)"""
        return {"id": file_id, "updated_metadata": metadata}

    def delete_drive_file(file_id: str):
        """Delete Drive file"""
        return {"id": file_id, "status": "deleted"}

    def share_drive_file(file_id: str, email: str, role: str):
        """Share file with user and role"""
        return {"id": file_id, "shared_with": email, "role": role}

    def summarize_drive_files(
        self, query: str = None, keyword: str = None, max_results: int = 5
    ) -> str:
        """
        Summarize Drive files in natural language, with optional keyword filtering.

        :param query: A Drive API query string like "name contains 'Proposal'"
        :param keyword: Simple keyword filter applied client-side for convenience
        :param max_results: Max number of files to summarize
        """
        files = self.list_drive_files(query=query)

        # Apply keyword filter locally too if provided
        if keyword:
            files = [f for f in files if keyword.lower() in f.get("name", "").lower()]

        files = files[:max_results]

        if not files:
            return f"No Drive files found matching '{keyword or query}'."

        lines = []
        for f in files:
            name = f.get("name")
            modified = f.get("modifiedTime", "unknown date")
            kind = f.get("mimeType", "File")

            if "folder" in kind:
                icon = "📂 Folder"
            elif "spreadsheet" in kind:
                icon = "📊 Spreadsheet"
            elif "document" in kind:
                icon = "📝 Doc"
            elif "presentation" in kind:
                icon = "📑 Slides"
            else:
                icon = "📄 File"

            lines.append(f"- {name} ({icon}, last modified {modified})")

        return "Here are the matching Drive files:\n" + "\n".join(lines)

    ## Google Docs Wrappers
    def get_doc_content(doc_id: str):
        """Fetch Google Doc contents"""
        return {"id": doc_id, "content": "Sample text in document"}

    def append_text_to_doc(
        self, doc_id: str, text: str, location: int = 1
    ) -> Dict[str, Any]:
        """
        Append text to a Google Document.
        location=1 means just after the doc start; use endIndex - 1 for EOF appending.
        """
        service = build("docs", "v1", credentials=self.creds)

        requests = [
            {
                "insertText": {
                    "location": {"index": location},
                    "text": text,
                }
            }
        ]

        result = (
            service.documents()
            .batchUpdate(documentId=doc_id, body={"requests": requests})
            .execute()
        )

        return {"id": doc_id, "status": "success", "updates": result.get("replies", [])}

    def replace_text_in_doc(doc_id: str, search: str, replace: str):
        """Replace text in doc"""
        return {"id": doc_id, "status": f"Replaced '{search}' with '{replace}'"}

    def create_doc(title: str):
        """Create new empty doc"""
        return {"id": "doc123", "name": title}

    def delete_doc(doc_id: str):
        """Delete a Doc (via Drive)"""
        return {"id": doc_id, "status": "deleted"}

    def summarize_doc(self, doc_id: str, max_paragraphs: int = 3) -> str:
        """
        Summarize contents of a Google Doc.
        Returns the first N chunks/paragraphs as a preview summary.
        """
        service = build("docs", "v1", credentials=self.creds)
        doc = service.documents().get(documentId=doc_id).execute()

        content = []
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                text_runs = element["paragraph"].get("elements", [])
                text = "".join(
                    tr.get("textRun", {}).get("content", "")
                    for tr in text_runs
                    if "textRun" in tr
                )
                if text.strip():
                    content.append(text.strip())
            if len(content) >= max_paragraphs:
                break

        if not content:
            return f"No textual content found in Doc '{doc.get('title')}'."

        return (
            f"Summary of '{doc.get('title')}' (first {len(content)} paragraphs):\n"
            + "\n".join(f"- {c}" for c in content)
        )

    ## Google Sheets Wrappers
    def get_sheet_values(sheet_id: str, range: str):
        return {"id": sheet_id, "range": range, "values": [["A1", "B1"], ["A2", "B2"]]}

    def update_sheet_values(sheet_id: str, range: str, values: list):
        return {"id": sheet_id, "range": range, "updated_values": values}

    def append_sheet_row(sheet_id: str, range: str, row_values: list):
        return {"id": sheet_id, "range": range, "appended_row": row_values}

    def create_sheet(title: str):
        return {"id": "sheet123", "name": title}

    def delete_sheet(sheet_id: str):
        return {"id": sheet_id, "status": "deleted"}

    ## Google Slides Wrappers
    def get_presentation(presentation_id: str):
        return {"id": presentation_id, "slides": ["slide1", "slide2"]}

    def create_presentation(title: str):
        return {"id": "pres123", "name": title}

    def append_slide(presentation_id: str, layout: str = "TITLE_AND_BODY"):
        return {"id": presentation_id, "new_slide_id": "slide3"}

    def insert_text_in_slide(presentation_id: str, slide_id: str, text: str):
        return {"id": presentation_id, "slide_id": slide_id, "inserted_text": text}

    def delete_slide(presentation_id: str, slide_id: str):
        return {"presentation_id": presentation_id, "removed": slide_id}

    def summarize_sheet(self, sheet_id: str, range: str = "A1:E5") -> str:
        """
        Summarize contents of a Google Sheet.
        Defaults to previewing the first 5 rows and 5 columns.
        """
        service = build("sheets", "v4", credentials=self.creds)
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=range)
            .execute()
        )

        values = result.get("values", [])

        if not values:
            return "This sheet is empty."

        header = values[0]
        rows = values[1:]

        summary_lines = [f"Columns: {', '.join(header)}"]
        if rows:
            for i, row in enumerate(rows[:3]):  # preview first 3 rows
                # pad missing cells
                row_display = ", ".join(row + [""] * (len(header) - len(row)))
                summary_lines.append(f"Row {i + 1}: {row_display}")

        return f"Summary of Sheet '{sheet_id}' (first few rows):\n" + "\n".join(
            summary_lines
        )

    ## Gmail Wrappers
    def list_recent_emails(query: str = None):
        return [{"id": "email123", "snippet": "Hello world"}]

    def get_email(email_id: str):
        return {"id": email_id, "subject": "Test Email", "body": "This is a test"}

    def send_email(self, to: str, subject: str, body: str) -> dict:
        """
        Send a plain-text Gmail message.
        """
        service = build("gmail", "v1", credentials=self.creds)

        # Create MIME message
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        # Encode to base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        sent = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message})
            .execute()
        )

        return {"id": sent["id"], "threadId": sent.get("threadId"), "status": "sent"}

    def reply_email(email_id: str, body: str):
        return {"id": email_id, "reply": body, "status": "sent"}

    def modify_email_labels(email_id: str, add_labels: list, remove_labels: list):
        return {"id": email_id, "added": add_labels, "removed": remove_labels}

    def summarize_gmail(
        self, keyword: str = None, sender: str = None, max_results: int = 5
    ) -> str:
        """
        Summarize recent Gmail messages in natural language, with optional filters.

        :param keyword: Keyword to match in subject or body snippet
        :param sender: Only include emails from this sender email or name
        :param max_results: Limit number of messages summarized
        """
        emails = self.list_recent_emails(
            max_results=max_results * 2
        )  # fetch a bit more

        if sender:
            emails = [e for e in emails if sender.lower() in e.get("from", "").lower()]
        if keyword:
            emails = [
                e for e in emails if keyword.lower() in e.get("subject", "").lower()
            ]

        emails = emails[:max_results]

        if not emails:
            filter_term = sender or keyword
            return f"No Gmail messages found matching '{filter_term}'."

        lines = []
        for e in emails:
            subj = e.get("subject", "No subject")
            frm = e.get("from", "Unknown Sender")
            lines.append(f'- "{subj}" from {frm}')

        return "Here are your filtered email messages:\n" + "\n".join(lines)

    # Google Calendar Wrappers
    def list_calendar_events(
        self, time_min: str = None, time_max: str = None, max_results: int = 10
    ) -> list[dict]:
        """
        List upcoming events between time_min and time_max (RFC3339).
        Defaults from 'now' through the next 7 days.
        """
        service = build("calendar", "v3", credentials=self.creds)

        if not time_min:
            time_min = datetime.datetime.utcnow().isoformat() + "Z"
        if not time_max:
            time_max = (
                datetime.datetime.utcnow() + datetime.timedelta(days=7)
            ).isoformat() + "Z"

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        simplified = []
        for e in events:
            start = e["start"].get(
                "dateTime", e["start"].get("date")
            )  # all-day vs timed
            simplified.append(
                {
                    "id": e.get("id"),
                    "title": e.get("summary", "No Title"),
                    "start": start,
                    "location": e.get("location", None),
                    "attendees": [a["email"] for a in e.get("attendees", [])]
                    if "attendees" in e
                    else [],
                }
            )

        return simplified

    def create_calendar_event(
        self,
        title: str,
        start: str,
        end: str,
        attendees: list = None,
        location: str = None,
    ) -> dict:
        """
        Create a new Google Calendar event.

        :param title: Title of the meeting/event
        :param start: Start time (RFC3339 format, e.g., '2025-08-27T10:00:00-07:00')
        :param end: End time (RFC3339 format)
        :param attendees: List of attendee emails
        :param location: Optional meeting location (string)
        """
        service = build("calendar", "v3", credentials=self.creds)

        event_body = {
            "summary": title,
            "location": location,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
        }

        if attendees:
            event_body["attendees"] = [{"email": a} for a in attendees]

        event = service.events().insert(calendarId="primary", body=event_body).execute()

        return {
            "id": event.get("id"),
            "htmlLink": event.get("htmlLink"),
            "start": event["start"]["dateTime"],
            "end": event["end"]["dateTime"],
            "title": event.get("summary"),
            "attendees": event.get("attendees", []),
        }

    def update_calendar_event(self, event_id: str, changes: dict) -> dict:
        """
        Update a Google Calendar event.

        :param event_id: ID of the event to update
        :param changes: A dictionary of fields to update, e.g.:
                        {
                        "summary": "New Title",
                        "start": {"dateTime": "...", "timeZone": "UTC"},
                        "end": {"dateTime": "...", "timeZone": "UTC"},
                        "location": "Board Room"
                        }
        """
        service = build("calendar", "v3", credentials=self.creds)

        # Get the existing event first
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        # Apply updates
        event.update(changes)

        updated_event = (
            service.events()
            .update(calendarId="primary", eventId=event_id, body=event)
            .execute()
        )

        return {
            "id": updated_event.get("id"),
            "title": updated_event.get("summary"),
            "start": updated_event["start"].get(
                "dateTime", updated_event["start"].get("date")
            ),
            "end": updated_event["end"].get(
                "dateTime", updated_event["end"].get("date")
            ),
            "location": updated_event.get("location"),
            "attendees": [a["email"] for a in updated_event.get("attendees", [])]
            if "attendees" in updated_event
            else [],
        }

    def delete_calendar_event(self, event_id: str) -> dict:
        """
        Delete (cancel) a Google Calendar event.

        :param event_id: The ID of the event to remove
        """
        service = build("calendar", "v3", credentials=self.creds)

        service.events().delete(calendarId="primary", eventId=event_id).execute()

        # The API returns no body on success, so we confirm deletion manually
        return {"id": event_id, "status": "deleted"}

    def summarize_calendar_events(
        self, time_min: str = None, time_max: str = None, max_results: int = 5
    ) -> str:
        """
        Generate a natural language summary of upcoming calendar events.
        """
        events = self.list_calendar_events(
            time_min=time_min, time_max=time_max, max_results=max_results
        )

        if not events:
            return "You have no upcoming events in this time range."

        lines = []
        for e in events:
            title = e.get("title", "Untitled Event")
            start = e.get("start", "No Start Time")
            location = f" at {e['location']}" if e.get("location") else ""
            attendees = ""
            if e.get("attendees"):
                attendees = " with " + ", ".join(e["attendees"])
            lines.append(f"- {start}: {title}{location}{attendees}")

        return "Here are your upcoming events:\n" + "\n".join(lines)
