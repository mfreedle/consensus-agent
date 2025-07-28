"""
title: GPT-4.1 Chat Agent & Google Workspace Pipe (OAuth)
author: rthidden
author_url: https://hiddendigitalaix.com
git_        # Construct OAuth 2.0 v2 URL manually
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": "http://localhost:19328/google-oauth-callback.html",
            "scope": " ".join(self.valves.SCOPES),
            "state": user_id,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent"  # Force consent to ensure refresh token
        }://github.com/rthidden/google-workspace-pipe.git
description: This pipe acts as a chat agent using OpenAI GPT-4.1 (Responses API) and can perform Google Drive, Docs, Sheets, and Slides actions using OAuth user authentication.
required_open_webui_version: 0.6.18
requirements: openai, google-auth, google-api-python-client, google-auth-httplib2, google-auth-oauthlib, requests, pydantic
version: 0.5.0
licence: MIT
"""

import json
import os
import time
from typing import Any, Generator, Union

import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pydantic import BaseModel, Field


class Pipe:
    class Valves(BaseModel):
        OPENAI_API_KEY: str = Field(
            default="sk-proj-...", description="Your OpenAI API key for GPT-4.1"
        )
        OAUTH_CREDENTIALS_FILE: str = Field(
            default="data/opt/oauth_credentials.json",
            description="Path to your Google OAuth client credentials JSON file",
        )
        TOKEN_STORAGE_DIR: str = Field(
            default="data/opt/tokens",
            description="Directory to store user OAuth tokens",
        )
        SCOPES: list = Field(
            default=[
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/presentations",
            ],
            description="Google API scopes to request",
        )

    def __init__(self):
        self.valves = self.Valves()
        # Ensure token storage directory exists
        os.makedirs(self.valves.TOKEN_STORAGE_DIR, exist_ok=True)

    def pipes(self):
        return [
            {
                "id": "google_workspace_gpt41",
                "name": "🔗 Google Workspace GPT-4.1 (Drive, Docs, Sheets, Slides)",
            }
        ]

    def get_user_credentials(self, user_id: str):
        """Get or create OAuth credentials for a user"""
        token_file = os.path.join(
            self.valves.TOKEN_STORAGE_DIR, f"{user_id}_token.json"
        )

        print(f"[DEBUG] Looking for token file: {token_file}")
        print(f"[DEBUG] Token file exists: {os.path.exists(token_file)}")

        creds = None
        # Load existing token
        if os.path.exists(token_file):
            try:
                from google.oauth2.credentials import Credentials

                with open(token_file, "r") as token:
                    creds_data = json.load(token)
                    creds = Credentials.from_authorized_user_info(
                        creds_data, self.valves.SCOPES
                    )
                    print(f"[DEBUG] Successfully loaded credentials for user {user_id}")
            except Exception as e:
                print(f"[DEBUG] Error loading existing token: {e}")

        # Refresh token if needed
        if creds and creds.expired and creds.refresh_token:
            try:
                from google.auth.transport.requests import Request

                creds.refresh(Request())
                # Save refreshed token
                with open(token_file, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None

        # If no valid credentials, need to authenticate
        if not creds or not creds.valid:
            print(f"[DEBUG] No valid credentials found for user {user_id}")
            print(f"[DEBUG] Creds exists: {creds is not None}")
            if creds:
                print(f"[DEBUG] Creds valid: {creds.valid}")
                print(f"[DEBUG] Creds expired: {creds.expired}")
            return None

        return creds

    def get_auth_url(self, user_id: str) -> str:
        """Generate OAuth authorization URL for user using v2 endpoint"""
        import json
        import urllib.parse

        # Load client secrets to get client_id
        with open(self.valves.OAUTH_CREDENTIALS_FILE, "r") as f:
            client_secrets = json.load(f)

        # Handle both 'web' and 'installed' credential types
        if "web" in client_secrets:
            client_id = client_secrets["web"]["client_id"]
        elif "installed" in client_secrets:
            client_id = client_secrets["installed"]["client_id"]
        else:
            raise ValueError(
                "Invalid OAuth credentials file format. Expected 'web' or 'installed' key."
            )

        # Construct OAuth 2.0 v2 URL manually
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": "http://localhost:19328/google-oauth-callback.html",
            "scope": " ".join(self.valves.SCOPES),
            "state": user_id,
            "access_type": "offline",
            "include_granted_scopes": "true",
        }

        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urllib.parse.urlencode(params)
        )
        return auth_url

    def handle_auth_callback(self, code: str, user_id: str) -> dict:
        """Handle OAuth callback and store user credentials"""
        try:
            from google_auth_oauthlib.flow import Flow

            # Create flow with all possible scopes to avoid scope mismatch
            all_scopes = [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/presentations",
            ]

            flow = Flow.from_client_secrets_file(
                self.valves.OAUTH_CREDENTIALS_FILE,
                scopes=all_scopes,
                redirect_uri="http://localhost:19328/google-oauth-callback.html",
            )

            flow.fetch_token(code=code)
            creds = flow.credentials

            # Debug: Check if we have a refresh token
            creds_json = json.loads(creds.to_json())
            print(f"[DEBUG] Credentials obtained for user {user_id}")
            print(f"[DEBUG] Has refresh token: {'refresh_token' in creds_json}")
            print(f"[DEBUG] Token expiry: {creds_json.get('expiry', 'None')}")

            # Save credentials
            token_file = os.path.join(
                self.valves.TOKEN_STORAGE_DIR, f"{user_id}_token.json"
            )
            with open(token_file, "w") as token:
                token.write(creds.to_json())

            print(f"[DEBUG] Token saved to: {token_file}")

            return {
                "success": True,
                "message": "Authentication successful! You can now use Google Workspace features.",
            }
        except Exception as e:
            return {"success": False, "error": f"Authentication failed: {str(e)}"}

    def check_pending_oauth(self, user_id: str) -> bool:
        """Check if user has a pending OAuth code and process it"""
        pending_file = os.path.join(
            self.valves.TOKEN_STORAGE_DIR, f"{user_id}_pending_oauth.json"
        )

        if os.path.exists(pending_file):
            try:
                with open(pending_file, "r") as f:
                    oauth_data = json.load(f)

                code = oauth_data.get("code")
                timestamp = oauth_data.get("timestamp", 0)

                # Check if code is not too old (10 minutes max)
                if time.time() - timestamp < 600 and code:
                    print(f"[DEBUG] Processing pending OAuth code for user {user_id}")
                    result = self.handle_auth_callback(code, user_id)

                    # Remove pending file after processing
                    os.remove(pending_file)

                    return result.get("success", False)
                else:
                    # Remove expired pending file
                    os.remove(pending_file)
                    print(f"[DEBUG] Expired OAuth code removed for user {user_id}")
            except Exception as e:
                print(f"[DEBUG] Error processing pending OAuth: {e}")
                try:
                    os.remove(pending_file)
                except Exception:
                    pass

        return False

    def pipe(self, body: dict, __user__: dict):
        print(
            f"[DEBUG] Google Workspace Pipe called with model: {body.get('model', 'unknown')}"
        )
        print(f"[DEBUG] User: {(__user__ or {}).get('email', 'unknown')}")

        user_valves = (__user__ or {}).get("valves", {})
        api_key = user_valves.get("OPENAI_API_KEY") or self.valves.OPENAI_API_KEY
        if not api_key:
            return {"error": "OPENAI_API_KEY not set in user or global valves."}

        # Get user ID (use email or create a unique identifier)
        user_id = (
            (__user__ or {}).get("id")
            or (__user__ or {}).get("email")
            or "default_user"
        )

        # Handle OAuth authentication flow
        action = body.get("action")
        if action == "auth_start":
            auth_url = self.get_auth_url(user_id)
            return {
                "auth_url": auth_url,
                "message": f"Please visit this URL to authenticate: {auth_url}",
            }
        elif action == "auth_callback":
            code = body.get("code")
            if not code or not isinstance(code, str):
                return {
                    "success": False,
                    "error": "Invalid authorization code provided",
                }
            return self.handle_auth_callback(code, user_id)
        elif action:
            # Check if user is authenticated for Google Workspace actions
            creds = self.get_user_credentials(user_id)
            if not creds:
                auth_url = self.get_auth_url(user_id)
                return {
                    "error": "Google authentication required",
                    "auth_url": auth_url,
                    "message": f"Please authenticate first by visiting: {auth_url}",
                }
            return self.google_workspace_action(action, body, creds)
        else:
            # Check if user is sending an OAuth code in the message
            messages = body.get("messages", [])
            if messages:
                last_message = messages[-1].get("content", "")

                # Look for OAuth code patterns in the message
                import re

                oauth_patterns = [
                    r"Complete authentication with code:\s*([A-Za-z0-9\-._~/%]{20,})",
                    r"authorization code:\s*([A-Za-z0-9\-._~/%]{20,})",
                    r"auth code:\s*([A-Za-z0-9\-._~/%]{20,})",
                    r"code:\s*([A-Za-z0-9\-._~/%]{20,})",
                ]

                for pattern in oauth_patterns:
                    match = re.search(pattern, last_message, re.IGNORECASE)
                    if match:
                        oauth_code = match.group(1)
                        print(
                            f"[DEBUG] Detected OAuth code in message for user {user_id}"
                        )

                        # Process the OAuth code
                        auth_result = self.handle_auth_callback(oauth_code, user_id)
                        if auth_result.get("success"):
                            return "🎉 **Authentication successful!** Your Google Workspace account is now connected. You can now ask me to list your files, create documents, or manage your Google Drive, Docs, Sheets, and Slides."
                        else:
                            return f"❌ **Authentication failed:** {auth_result.get('error', 'Unknown error')}"

            return self.openai_responses_api(body, __user__, user_id)

    def get_google_workspace_tools(self):
        """Define the Google Workspace functions that the model can call"""
        return [
            {
                "type": "function",
                "name": "list_drive_files",
                "description": "List files in Google Drive. Shows up to 50 files by default.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to filter files (optional). Example: 'name contains \"report\"' or 'mimeType=\"application/pdf\"'",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of files to return (default: 50, max: 100)",
                        },
                    },
                },
            },
            {
                "type": "function",
                "name": "read_drive_file",
                "description": "Get details about a specific file in Google Drive",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID",
                        }
                    },
                    "required": ["file_id"],
                },
            },
            {
                "type": "function",
                "name": "create_google_doc",
                "description": "Create a new Google Document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the document",
                        }
                    },
                    "required": ["title"],
                },
            },
            {
                "type": "function",
                "name": "read_google_doc",
                "description": "Read the content of a Google Document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "The Google Document ID",
                        }
                    },
                    "required": ["doc_id"],
                },
            },
            {
                "type": "function",
                "name": "create_google_sheet",
                "description": "Create a new Google Spreadsheet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the spreadsheet",
                        }
                    },
                    "required": ["title"],
                },
            },
            {
                "type": "function",
                "name": "read_google_sheet",
                "description": "Read data from a Google Spreadsheet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sheet_id": {
                            "type": "string",
                            "description": "The Google Spreadsheet ID",
                        },
                        "range_name": {
                            "type": "string",
                            "description": "The range to read (e.g., 'Sheet1!A1:C10' or 'Sheet1')",
                        },
                    },
                    "required": ["sheet_id", "range_name"],
                },
            },
        ]

    def openai_responses_api(
        self, body: dict, __user__: dict, user_id: str
    ) -> Union[str, dict, Generator[str, Any, None]]:
        # Get fields from body
        original_model = body.get("model", "gpt-4o")

        # Map our pipe name to actual OpenAI model
        if "google_workspace" in original_model:
            model_id = "gpt-4o"  # Use GPT-4o which supports function calling
        elif original_model == "google_workspace_pipe":
            model_id = "gpt-4o"
        elif original_model == "google_workspace_gpt41":
            model_id = "gpt-4o"
        else:
            model_id = "gpt-4o"  # Default to gpt-4o for function calling support

        input_messages = (
            body.get("messages")
            or body.get("input")
            or [{"role": "user", "content": body.get("prompt", "")}]
        )

        instructions = body.get("instructions")
        stream = body.get("stream", False)

        api_key = self.valves.OPENAI_API_KEY

        # If individual user key is set, prefer it
        user_key = (__user__ or {}).get("valves", {}).get("OPENAI_API_KEY")
        if user_key:
            api_key = user_key

        print(f"[DEBUG] Original model: {original_model}")
        print(f"[DEBUG] Mapped model: {model_id}")
        print(f"[DEBUG] API key available: {bool(api_key)}")
        print(
            f"[DEBUG] API key (first 10 chars): {api_key[:10] if api_key else 'None'}..."
        )

        # Defensive: If api_key is missing, always return error dict
        if not api_key:
            return {"error": "OPENAI_API_KEY not set in user or global valves."}

        # Defensive: If input_messages is None or empty, return error dict
        if not input_messages or (
            isinstance(input_messages, list) and len(input_messages) == 0
        ):
            return {"error": "No input messages provided."}

        # Format input for OpenAI Responses API
        if isinstance(input_messages, list) and len(input_messages) > 0:
            # Convert messages to a simple string input for Responses API
            input_text = "\n".join(
                [
                    f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                    for msg in input_messages
                    if msg.get("content")
                ]
            )
        else:
            input_text = str(input_messages)

        try:
            # Prepare headers with Bearer token
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # Prepare payload for Responses API with Google Workspace tools
            payload = {
                "model": model_id,
                "input": input_text,
                "tools": self.get_google_workspace_tools(),
            }

            if instructions:
                payload["instructions"] = instructions
            if stream:
                payload["stream"] = stream

            # Make request to OpenAI Responses API
            response = requests.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
                stream=stream,
                timeout=30,
            )

            if response.status_code != 200:
                error_text = response.text
                error_msg = f"OpenAI API Error: {response.status_code} - {error_text}"
                return {"error": error_msg}

            if stream:
                # Return streaming generator for Open WebUI with function calling support
                return self.handle_streaming_with_functions(
                    response, headers, payload, user_id
                )
            else:
                return self.handle_non_streaming_with_functions(
                    response, headers, payload, user_id
                )

        except Exception as e:
            error_msg = f"OpenAI: {type(e).__name__}: {e}"
            return {"error": error_msg}

    def handle_streaming_with_functions(self, response, headers, payload, user_id: str):
        """Handle streaming responses with function calling support"""
        function_calls = {}  # Store function calls by ID

        def generate():
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        try:
                            if line_str.strip() == "data: [DONE]":
                                break
                            data = json.loads(line_str[6:])

                            # Handle function call events
                            if data.get("type") == "response.output_item.added":
                                item = data.get("item", {})
                                if item.get("type") == "function_call":
                                    func_id = item.get("id")
                                    function_calls[func_id] = {
                                        "name": item.get("name"),
                                        "arguments": "",
                                        "call_id": item.get("call_id"),
                                    }
                                    continue

                            elif (
                                data.get("type")
                                == "response.function_call_arguments.delta"
                            ):
                                func_id = data.get("item_id")
                                if func_id in function_calls:
                                    function_calls[func_id]["arguments"] += data.get(
                                        "delta", ""
                                    )
                                continue

                            elif (
                                data.get("type")
                                == "response.function_call_arguments.done"
                            ):
                                func_id = data.get("item_id")
                                if func_id in function_calls:
                                    function_calls[func_id]["arguments"] = data.get(
                                        "arguments", ""
                                    )
                                    # Execute the function call
                                    result = self.execute_function_call(
                                        function_calls[func_id], user_id
                                    )
                                    # Continue the conversation with the function result
                                    yield from self.continue_with_function_result(
                                        function_calls[func_id],
                                        result,
                                        headers,
                                        payload,
                                    )
                                continue

                            # Handle regular text content
                            content = None
                            if (
                                data.get("type") == "response.output_text.delta"
                                and "delta" in data
                            ):
                                content = data["delta"]
                            elif "choices" in data and len(data["choices"]) > 0:
                                choice = data["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    content = choice["delta"]["content"]

                            # Skip final complete content events to avoid duplication
                            if data.get("type") in [
                                "response.output_text.done",
                                "response.content_part.done",
                                "response.output_item.done",
                                "response.completed",
                            ]:
                                continue

                            if content:
                                yield content

                        except json.JSONDecodeError:
                            continue

        return generate()

    def handle_non_streaming_with_functions(
        self, response, headers, payload, user_id: str
    ):
        """Handle non-streaming responses with function calling support"""
        response_data = response.json()

        # Check if the response contains function calls
        if "output" in response_data and len(response_data["output"]) > 0:
            output_item = response_data["output"][0]

            # Check if this is a function call
            if output_item.get("type") == "function_call":
                func_call = {
                    "name": output_item.get("name"),
                    "arguments": output_item.get("arguments", ""),
                    "call_id": output_item.get("call_id"),
                }

                # Execute the function
                result = self.execute_function_call(func_call, user_id)

                # Continue the conversation with the function result
                return self.continue_conversation_with_result(
                    func_call, result, headers, payload
                )

            # Regular text response
            elif "content" in output_item and len(output_item["content"]) > 0:
                content_item = output_item["content"][0]
                if "text" in content_item:
                    return content_item["text"]

        # Fallback content extraction
        content = (
            response_data.get("output_text")
            or response_data.get("content")
            or str(response_data)
        )

        return content if content else "No response content found"

    def execute_function_call(self, func_call, user_id: str):
        """Execute a function call and return the result"""
        try:
            # Get user credentials for the function call
            creds = self.get_user_credentials(user_id)
            if not creds:
                return {
                    "error": "Google authentication required",
                    "auth_url": self.get_auth_url(user_id),
                    "message": "Please authenticate first by visiting the auth URL",
                }

            function_name = func_call["name"]
            arguments = (
                json.loads(func_call["arguments"]) if func_call["arguments"] else {}
            )

            if function_name == "list_drive_files":
                return self.google_workspace_action("list_drive", arguments, creds)
            elif function_name == "read_drive_file":
                return self.google_workspace_action("read_drive", arguments, creds)
            elif function_name == "create_google_doc":
                return self.google_workspace_action("create_doc", arguments, creds)
            elif function_name == "read_google_doc":
                return self.google_workspace_action("read_doc", arguments, creds)
            elif function_name == "create_google_sheet":
                return self.google_workspace_action("create_sheet", arguments, creds)
            elif function_name == "read_google_sheet":
                return self.google_workspace_action("read_sheet", arguments, creds)
            else:
                return {"error": f"Unknown function: {function_name}"}

        except Exception as e:
            return {"error": f"Function execution failed: {type(e).__name__}: {e}"}

    def continue_with_function_result(self, func_call, result, headers, payload):
        """Continue the streaming conversation with function result"""
        # For streaming, we'll yield the function result and continue
        yield f"\n[Function {func_call['name']} executed: {json.dumps(result, indent=2)}]\n"

    def continue_conversation_with_result(self, func_call, result, headers, payload):
        """Continue the non-streaming conversation with function result"""
        # Create a follow-up request with the function result
        function_result_text = (
            f"Function {func_call['name']} result: {json.dumps(result, indent=2)}"
        )

        # Update the payload with the function result
        updated_payload = payload.copy()
        updated_payload["input"] += (
            f"\n\n{function_result_text}\n\nBased on this function result, please provide a helpful response to the user."
        )
        updated_payload["stream"] = False

        # Remove tools from follow-up request to get final response
        if "tools" in updated_payload:
            del updated_payload["tools"]

        try:
            response = requests.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=updated_payload,
                timeout=30,
            )

            if response.status_code == 200:
                response_data = response.json()
                if "output" in response_data and len(response_data["output"]) > 0:
                    output_item = response_data["output"][0]
                    if "content" in output_item and len(output_item["content"]) > 0:
                        content_item = output_item["content"][0]
                        if "text" in content_item:
                            return content_item["text"]

            return f"Function executed successfully: {json.dumps(result, indent=2)}"

        except Exception as e:
            return f"Function executed with result: {json.dumps(result, indent=2)}\n\nNote: Could not generate follow-up response due to error: {e}"

    def google_workspace_action(self, action: str, body: dict, creds) -> dict:
        try:
            if action == "upload_drive":
                service = build("drive", "v3", credentials=creds)
                filename = body["filename"]
                filepath = body["filepath"]
                file_metadata = {"name": filename}
                media = MediaFileUpload(filepath, resumable=True)
                file = (
                    service.files()
                    .create(body=file_metadata, media_body=media, fields="id")
                    .execute()
                )
                return {"file_id": file.get("id")}

            elif action == "list_drive":
                service = build("drive", "v3", credentials=creds)
                query = body.get("query")
                max_results = body.get("max_results", 50)

                # Build the request parameters
                request_params = {
                    "pageSize": min(max_results, 100),  # API max is 100
                    "fields": "files(id, name, mimeType, size, modifiedTime, createdTime, webViewLink)",
                }

                if query:
                    request_params["q"] = query

                results = service.files().list(**request_params).execute()
                files = results.get("files", [])

                return {
                    "files": files,
                    "count": len(files),
                    "message": f"Found {len(files)} files in Google Drive",
                }

            elif action == "read_drive":
                service = build("drive", "v3", credentials=creds)
                file_id = body["file_id"]
                file = (
                    service.files()
                    .get(
                        fileId=file_id,
                        fields="id, name, mimeType, size, modifiedTime, createdTime, webViewLink, description",
                    )
                    .execute()
                )
                return file

            elif action == "create_doc":
                service = build("docs", "v1", credentials=creds)
                title = body["title"]
                doc = service.documents().create(body={"title": title}).execute()
                doc_id = doc.get("documentId")
                return {
                    "documentId": doc_id,
                    "title": title,
                    "webViewLink": f"https://docs.google.com/document/d/{doc_id}/edit",
                    "message": f"Successfully created Google Doc: {title}",
                }

            elif action == "read_doc":
                service = build("docs", "v1", credentials=creds)
                doc_id = body["doc_id"]
                doc = service.documents().get(documentId=doc_id).execute()

                # Extract text content from the document
                content_text = ""
                if "body" in doc and "content" in doc["body"]:
                    for element in doc["body"]["content"]:
                        if "paragraph" in element:
                            paragraph = element["paragraph"]
                            if "elements" in paragraph:
                                for elem in paragraph["elements"]:
                                    if (
                                        "textRun" in elem
                                        and "content" in elem["textRun"]
                                    ):
                                        content_text += elem["textRun"]["content"]

                return {
                    "documentId": doc_id,
                    "title": doc.get("title", ""),
                    "content": content_text,
                    "message": f"Successfully read Google Doc content ({len(content_text)} characters)",
                }

            elif action == "edit_doc":
                service = build("docs", "v1", credentials=creds)
                doc_id = body["doc_id"]
                requests_ = body["requests"]
                result = (
                    service.documents()
                    .batchUpdate(documentId=doc_id, body={"requests": requests_})
                    .execute()
                )
                return result

            elif action == "create_sheet":
                service = build("sheets", "v4", credentials=creds)
                title = body["title"]
                sheet = (
                    service.spreadsheets()
                    .create(body={"properties": {"title": title}})
                    .execute()
                )
                sheet_id = sheet.get("spreadsheetId")
                return {
                    "spreadsheetId": sheet_id,
                    "title": title,
                    "webViewLink": f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit",
                    "message": f"Successfully created Google Sheet: {title}",
                }

            elif action == "read_sheet":
                service = build("sheets", "v4", credentials=creds)
                sheet_id = body["sheet_id"]
                range_name = body["range_name"]
                result = (
                    service.spreadsheets()
                    .values()
                    .get(spreadsheetId=sheet_id, range=range_name)
                    .execute()
                )
                values = result.get("values", [])
                return {
                    "spreadsheetId": sheet_id,
                    "range": range_name,
                    "values": values,
                    "rowCount": len(values),
                    "message": f"Successfully read {len(values)} rows from Google Sheet",
                }

            elif action == "edit_sheet":
                service = build("sheets", "v4", credentials=creds)
                sheet_id = body["sheet_id"]
                range_name = body["range_name"]
                values = body["values"]
                body_ = {"values": values}
                result = (
                    service.spreadsheets()
                    .values()
                    .update(
                        spreadsheetId=sheet_id,
                        range=range_name,
                        valueInputOption="RAW",
                        body=body_,
                    )
                    .execute()
                )
                return result

            elif action == "create_slide":
                service = build("slides", "v1", credentials=creds)
                title = body["title"]
                slide = service.presentations().create(body={"title": title}).execute()
                return {"presentationId": slide.get("presentationId")}

            elif action == "read_slide":
                service = build("slides", "v1", credentials=creds)
                slide_id = body["slide_id"]
                slide = service.presentations().get(presentationId=slide_id).execute()
                return slide

            elif action == "edit_slide":
                service = build("slides", "v1", credentials=creds)
                slide_id = body["slide_id"]
                requests_ = body["requests"]
                result = (
                    service.presentations()
                    .batchUpdate(presentationId=slide_id, body={"requests": requests_})
                    .execute()
                )
                return result

            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            return {"error": f"Google Workspace: {type(e).__name__}: {e}"}
