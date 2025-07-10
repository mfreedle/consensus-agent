from datetime import datetime
from typing import Any, List, Optional

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


# Enhanced schemas for LLM editing capabilities
class GoogleDocumentEdit(BaseModel):
    """Schema for editing Google Document content"""
    content: str


class GoogleDocumentCreate(BaseModel):
    """Schema for creating a new Google Document"""
    title: str
    content: Optional[str] = ""


class GoogleSpreadsheetContent(BaseModel):
    """Schema for Google Spreadsheet content"""
    spreadsheet_id: str
    title: str
    sheets: dict  # Sheet name -> List of rows
    sheet_count: int
    web_view_link: str


class GoogleSpreadsheetEdit(BaseModel):
    """Schema for editing Google Spreadsheet content"""
    sheet_name: str
    range_name: str  # e.g., "A1:C10"
    values: List[List[Any]]  # 2D array of values


class GoogleSpreadsheetCreate(BaseModel):
    """Schema for creating a new Google Spreadsheet"""
    title: str


class GooglePresentationContent(BaseModel):
    """Schema for Google Slides presentation content"""
    presentation_id: str
    title: str
    slides: List[dict]  # List of slide data
    slide_count: int
    web_view_link: str


class GooglePresentationCreate(BaseModel):
    """Schema for creating a new Google Slides presentation"""
    title: str


class GoogleSlideCreate(BaseModel):
    """Schema for adding a slide to a presentation"""
    title: str
    content: str


class GoogleFileOperation(BaseModel):
    """Schema for file operation responses"""
    success: bool
    message: str
    file_id: Optional[str] = None
    web_view_link: Optional[str] = None


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
