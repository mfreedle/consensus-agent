from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class GoogleAuthURL(BaseModel):
    """Schema for Google OAuth authorization URL response"""
    auth_url: str
    state: str


class GoogleTokens(BaseModel):
    """Schema for Google OAuth tokens"""
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[str] = None
    scope: Optional[str] = None


class GoogleDriveFile(BaseModel):
    """Schema for Google Drive file information"""
    id: str
    name: str
    type: str  # document, spreadsheet, presentation, folder, file
    mime_type: str
    modified_time: Optional[str] = None
    web_view_link: Optional[str] = None
    owners: List[dict] = []


class GoogleDriveFileList(BaseModel):
    """Schema for Google Drive file list response"""
    files: List[GoogleDriveFile]
    total_count: int


class GoogleDocumentContent(BaseModel):
    """Schema for Google Document content"""
    document_id: str
    title: str
    content: str
    revision_id: Optional[str] = None


class GoogleDriveConnection(BaseModel):
    """Schema for Google Drive connection status"""
    connected: bool
    user_email: Optional[str] = None
    connection_date: Optional[datetime] = None
    scopes: List[str] = []


class GoogleOAuthCallback(BaseModel):
    """Schema for Google OAuth callback data"""
    code: str
    state: str
    scope: Optional[str] = None


class GoogleDriveError(BaseModel):
    """Schema for Google Drive error responses"""
    error: str
    error_description: Optional[str] = None
    error_code: Optional[int] = None
