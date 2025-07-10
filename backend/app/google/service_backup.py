from datetime import datetime, timezone
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import Settings


class GoogleDriveService:
    """Service for Google Drive OAuth and API operations"""
    
    # OAuth scopes for Google Drive and Docs
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client_config = {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri]
            }
        }
    
    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """
        Generate Google OAuth authorization URL
        
        Returns:
            tuple: (authorization_url, state)
        """
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            state=state
        )
        flow.redirect_uri = self.settings.google_redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        return authorization_url, state
    
    def exchange_code_for_tokens(self, authorization_code: str, state: str) -> Dict:
        """
        Exchange authorization code for access tokens
        
        Args:
            authorization_code: The authorization code from OAuth callback
            state: The state parameter from OAuth callback
            
        Returns:
            Dict containing token information
        """
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.SCOPES,
            state=state
        )
        flow.redirect_uri = self.settings.google_redirect_uri
        
        # Exchange code for tokens
        flow.fetch_token(code=authorization_code)
        
        credentials = flow.credentials
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            "scope": " ".join(credentials._scopes) if credentials._scopes else ""
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dict containing new token information
        """
        credentials = Credentials.from_authorized_user_info({
            "refresh_token": refresh_token,
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret
        })
        
        # Refresh the token
        credentials.refresh(Request())
        
        return {
            "access_token": credentials.token,
            "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def get_credentials_from_tokens(self, access_token: str, refresh_token: Optional[str] = None) -> Credentials:
        """
        Create Google credentials object from stored tokens
        
        Args:
            access_token: The access token
            refresh_token: The refresh token (optional)
            
        Returns:
            Google Credentials object
        """
        token_info = {
            "token": access_token,
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret
        }
        
        if refresh_token:
            token_info["refresh_token"] = refresh_token
            
        return Credentials.from_authorized_user_info(token_info)
    
    async def list_drive_files(self, access_token: str, refresh_token: Optional[str] = None, 
                              file_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        List files from Google Drive
        
        Args:
            access_token: User's access token
            refresh_token: User's refresh token
            file_type: Filter by file type (document, spreadsheet, presentation)
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('drive', 'v3', credentials=credentials)
            
            # Build query based on file type
            query = "trashed=false"
            if file_type == "document":
                query += " and mimeType='application/vnd.google-apps.document'"
            elif file_type == "spreadsheet":
                query += " and mimeType='application/vnd.google-apps.spreadsheet'"
            elif file_type == "presentation":
                query += " and mimeType='application/vnd.google-apps.presentation'"
            
            # Execute the query
            results = service.files().list(
                q=query,
                pageSize=limit,
                fields="files(id,name,mimeType,modifiedTime,webViewLink,owners)"
            ).execute()
            
            files = results.get('files', [])
            
            # Format file information
            formatted_files = []
            for file in files:
                formatted_files.append({
                    "id": file["id"],
                    "name": file["name"],
                    "type": self._get_file_type_from_mime(file["mimeType"]),
                    "mime_type": file["mimeType"],
                    "modified_time": file.get("modifiedTime"),
                    "web_view_link": file.get("webViewLink"),
                    "owners": file.get("owners", [])
                })
            
            return formatted_files
            
        except HttpError as error:
            raise Exception(f"Google Drive API error: {error}")
    
    async def get_document_content(self, document_id: str, access_token: str, 
                                  refresh_token: Optional[str] = None) -> Dict:
        """
        Get content from a Google Document
        
        Args:
            document_id: The Google Document ID
            access_token: User's access token
            refresh_token: User's refresh token
            
        Returns:
            Dict containing document content and metadata
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('docs', 'v1', credentials=credentials)
            
            # Get document content
            document = service.documents().get(documentId=document_id).execute()
            
            # Extract text content
            content = self._extract_text_from_document(document)
            
            return {
                "document_id": document_id,
                "title": document.get("title", "Untitled"),
                "content": content,
                "revision_id": document.get("revisionId"),
                "document_style": document.get("documentStyle", {})
            }
            
        except HttpError as error:
            raise Exception(f"Google Docs API error: {error}")
    
    def _get_file_type_from_mime(self, mime_type: str) -> str:
        """Convert MIME type to readable file type"""
        mime_mapping = {
            "application/vnd.google-apps.document": "document",
            "application/vnd.google-apps.spreadsheet": "spreadsheet", 
            "application/vnd.google-apps.presentation": "presentation",
            "application/vnd.google-apps.folder": "folder"
        }
        return mime_mapping.get(mime_type, "file")
    
    def _extract_text_from_document(self, document: Dict) -> str:
        """Extract plain text from Google Document structure"""
        content = ""
        
        if "body" in document and "content" in document["body"]:
            for element in document["body"]["content"]:
                if "paragraph" in element:
                    paragraph = element["paragraph"]
                    if "elements" in paragraph:
                        for elem in paragraph["elements"]:
                            if "textRun" in elem and "content" in elem["textRun"]:
                                content += elem["textRun"]["content"]
        
        return content

    async def edit_document_content(self, document_id: str, access_token: str,
                                    new_content: str, 
                                    refresh_token: Optional[str] = None) -> Dict:
        """
        Edit content in a Google Document
        
        Args:
            document_id: The Google Document ID
            access_token: User's access token
            new_content: New content to replace the document
            refresh_token: User's refresh token
            
        Returns:
            Dict containing success status and metadata
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('docs', 'v1', credentials=credentials)
            
            # Get current document to find content length
            document = service.documents().get(documentId=document_id).execute()
            
            # Calculate total content length
            content_length = 1  # Start with 1 to include the final newline
            if "body" in document and "content" in document["body"]:
                for element in document["body"]["content"]:
                    if "paragraph" in element:
                        paragraph = element["paragraph"]
                        if "elements" in paragraph:
                            for elem in paragraph["elements"]:
                                if "textRun" in elem and "content" in elem["textRun"]:
                                    content_length += len(elem["textRun"]["content"])
            
            # Create requests to replace all content
            requests = []
            
            # First, delete all existing content (except the last character to avoid error)
            if content_length > 1:
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': content_length - 1
                        }
                    }
                })
            
            # Then insert new content
            requests.append({
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': new_content
                }
            })
            
            # Execute the batch update
            service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return {
                "success": True,
                "document_id": document_id,
                "message": "Document updated successfully"
            }
            
        except HttpError as error:
            raise Exception(f"Google Docs API error: {error}")
        except Exception as e:
            raise Exception(f"Failed to edit document: {str(e)}")

    async def create_document(self, access_token: str, title: str, content: str = "",
                             refresh_token: Optional[str] = None) -> Dict:
        """
        Create a new Google Document
        
        Args:
            access_token: User's access token
            title: Title for the new document
            content: Initial content for the document
            refresh_token: User's refresh token
            
        Returns:
            Dict containing document information
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('docs', 'v1', credentials=credentials)
            
            # Create the document
            document = {
                'title': title
            }
            
            doc_result = service.documents().create(body=document).execute()
            document_id = doc_result.get('documentId')
            
            # Add content if provided
            if content:
                requests = [{
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                }]
                
                service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()
            
            return {
                "document_id": document_id,
                "title": title,
                "web_view_link": f"https://docs.google.com/document/d/{document_id}/edit",
                "success": True
            }
            
        except HttpError as error:
            raise Exception(f"Google Docs API error: {error}")

    async def get_spreadsheet_content(self, spreadsheet_id: str, access_token: str,
                                     refresh_token: Optional[str] = None) -> Dict:
        """
        Get content from a Google Spreadsheet
        
        Args:
            spreadsheet_id: The Google Spreadsheet ID
            access_token: User's access token
            refresh_token: User's refresh token
            
        Returns:
            Dict containing spreadsheet content and metadata
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('sheets', 'v4', credentials=credentials)
            
            # Get spreadsheet metadata
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            
            # Get all sheet data
            sheets_data = {}
            for sheet in spreadsheet.get('sheets', []):
                sheet_name = sheet['properties']['title']
                
                # Get values from the sheet
                range_name = f"'{sheet_name}'"
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name
                ).execute()
                
                values = result.get('values', [])
                sheets_data[sheet_name] = values
            
            return {
                "spreadsheet_id": spreadsheet_id,
                "title": spreadsheet.get("properties", {}).get("title", "Untitled"),
                "sheets": sheets_data,
                "sheet_count": len(spreadsheet.get('sheets', [])),
                "web_view_link": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            }
            
        except HttpError as error:
            raise Exception(f"Google Sheets API error: {error}")

    async def edit_spreadsheet_content(self, spreadsheet_id: str, access_token: str,
                                      sheet_name: str, range_name: str, values: List[List],
                                      refresh_token: Optional[str] = None) -> Dict:
        """
        Edit content in a Google Spreadsheet
        
        Args:
            spreadsheet_id: The Google Spreadsheet ID
            access_token: User's access token
            sheet_name: Name of the sheet to edit
            range_name: Range to update (e.g., 'A1:C10')
            values: 2D array of values to update
            refresh_token: User's refresh token
            
        Returns:
            Dict containing success status and metadata
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('sheets', 'v4', credentials=credentials)
            
            # Update the range
            full_range = f"'{sheet_name}'!{range_name}"
            body = {
                'values': values
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=full_range,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "updated_cells": result.get('updatedCells', 0),
                "updated_range": result.get('updatedRange', ''),
                "message": "Spreadsheet updated successfully"
            }
            
        except HttpError as error:
            raise Exception(f"Google Sheets API error: {error}")

    async def create_spreadsheet(self, access_token: str, title: str,
                                refresh_token: Optional[str] = None) -> Dict:
        """
        Create a new Google Spreadsheet
        
        Args:
            access_token: User's access token
            title: Title for the new spreadsheet
            refresh_token: User's refresh token
            
        Returns:
            Dict containing spreadsheet information
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('sheets', 'v4', credentials=credentials)
            
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            result = service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result['spreadsheetId']
            
            return {
                "spreadsheet_id": spreadsheet_id,
                "title": title,
                "web_view_link": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
                "success": True
            }
            
        except HttpError as error:
            raise Exception(f"Google Sheets API error: {error}")

    async def get_presentation_content(self, presentation_id: str, access_token: str,
                                      refresh_token: Optional[str] = None) -> Dict:
        """
        Get content from a Google Slides presentation
        
        Args:
            presentation_id: The Google Slides presentation ID
            access_token: User's access token
            refresh_token: User's refresh token
            
        Returns:
            Dict containing presentation content and metadata
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('slides', 'v1', credentials=credentials)
            
            # Get presentation
            presentation = service.presentations().get(presentationId=presentation_id).execute()
            
            # Extract text content from slides
            slides_content = []
            for slide in presentation.get('slides', []):
                slide_data = {
                    'slide_id': slide['objectId'],
                    'text_content': []
                }
                
                # Extract text from page elements
                for page_element in slide.get('pageElements', []):
                    if 'shape' in page_element and 'text' in page_element['shape']:
                        text_elements = page_element['shape']['text'].get('textElements', [])
                        for text_element in text_elements:
                            if 'textRun' in text_element:
                                slide_data['text_content'].append(text_element['textRun']['content'])
                
                slides_content.append(slide_data)
            
            return {
                "presentation_id": presentation_id,
                "title": presentation.get('title', 'Untitled'),
                "slides": slides_content,
                "slide_count": len(presentation.get('slides', [])),
                "web_view_link": f"https://docs.google.com/presentation/d/{presentation_id}/edit"
            }
            
        except HttpError as error:
            raise Exception(f"Google Slides API error: {error}")

    async def create_presentation(self, access_token: str, title: str,
                                 refresh_token: Optional[str] = None) -> Dict:
        """
        Create a new Google Slides presentation
        
        Args:
            access_token: User's access token
            title: Title for the new presentation
            refresh_token: User's refresh token
            
        Returns:
            Dict containing presentation information
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('slides', 'v1', credentials=credentials)
            
            presentation = {
                'title': title
            }
            
            result = service.presentations().create(body=presentation).execute()
            presentation_id = result['presentationId']
            
            return {
                "presentation_id": presentation_id,
                "title": title,
                "web_view_link": f"https://docs.google.com/presentation/d/{presentation_id}/edit",
                "success": True
            }
            
        except HttpError as error:
            raise Exception(f"Google Slides API error: {error}")

    async def add_slide_with_text(self, presentation_id: str, access_token: str,
                                 title: str, content: str,
                                 refresh_token: Optional[str] = None) -> Dict:
        """
        Add a new slide with text to a Google Slides presentation
        
        Args:
            presentation_id: The Google Slides presentation ID
            access_token: User's access token
            title: Title for the slide
            content: Content for the slide
            refresh_token: User's refresh token
            
        Returns:
            Dict containing success status and slide information
        """
        try:
            credentials = self.get_credentials_from_tokens(access_token, refresh_token)
            service = build('slides', 'v1', credentials=credentials)
            
            # Generate unique IDs
            slide_id = f"slide_{int(datetime.now().timestamp())}"
            title_id = f"title_{int(datetime.now().timestamp())}"
            content_id = f"content_{int(datetime.now().timestamp())}"
            
            requests = [
                # Create new slide
                {
                    'createSlide': {
                        'objectId': slide_id,
                        'slideLayoutReference': {
                            'predefinedLayout': 'TITLE_AND_BODY'
                        }
                    }
                },
                # Add title
                {
                    'insertText': {
                        'objectId': title_id,
                        'text': title
                    }
                },
                # Add content
                {
                    'insertText': {
                        'objectId': content_id,
                        'text': content
                    }
                }
            ]
            
            service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()
            
            return {
                "success": True,
                "presentation_id": presentation_id,
                "slide_id": slide_id,
                "message": "Slide added successfully"
            }
            
        except HttpError as error:
            raise Exception(f"Google Slides API error: {error}")
