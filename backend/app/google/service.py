import json
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
