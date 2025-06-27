import json
from datetime import datetime
from typing import Optional

from app.auth.dependencies import get_current_active_user
from app.config import Settings, settings
from app.database.connection import get_db
from app.google.service import GoogleDriveService
from app.models.user import User
from app.schemas.google import (
    GoogleAuthURL, GoogleDriveConnection, GoogleDriveError, GoogleDriveFile,
    GoogleDriveFileList, GoogleDocumentContent, GoogleOAuthCallback, GoogleTokens
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

router = APIRouter()

# Initialize Google Drive service
google_service = GoogleDriveService(settings)


@router.get("/auth", response_model=GoogleAuthURL)
async def google_auth_url(
    current_user: User = Depends(get_current_active_user)
):
    """Get Google OAuth authorization URL"""
    
    try:
        # Generate authorization URL with user ID as state for security
        auth_url, state = google_service.get_authorization_url(
            state=f"user:{current_user.id}"
        )
        
        return GoogleAuthURL(auth_url=auth_url, state=state)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Google authorization URL: {str(e)}"
        )


@router.post("/callback", response_model=GoogleTokens)
async def google_callback(
    callback_data: GoogleOAuthCallback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Handle Google OAuth callback and store tokens"""
    
    try:
        # Verify state parameter for security
        expected_state = f"user:{current_user.id}"
        if callback_data.state != expected_state:
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )
        
        # Exchange authorization code for tokens
        tokens = google_service.exchange_code_for_tokens(
            callback_data.code, 
            callback_data.state
        )
        
        # Parse token expiry
        token_expiry = None
        if tokens.get("token_expiry"):
            token_expiry = datetime.fromisoformat(tokens["token_expiry"].replace('Z', '+00:00'))
        
        # Update user with Google Drive tokens
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(
                google_drive_token=tokens["access_token"],
                google_refresh_token=tokens.get("refresh_token"),
                google_token_expiry=token_expiry
            )
        )
        await db.commit()
        
        return GoogleTokens(**tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Google OAuth callback: {str(e)}"
        )


@router.get("/connection", response_model=GoogleDriveConnection)
async def get_google_drive_connection_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get Google Drive connection status for current user"""
    
    connected = bool(current_user.google_drive_token and current_user.google_refresh_token)
    
    connection_info = GoogleDriveConnection(
        connected=connected,
        connection_date=current_user.google_token_expiry,
        scopes=google_service.SCOPES if connected else []
    )
    
    return connection_info


@router.delete("/disconnect")
async def disconnect_google_drive(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Disconnect Google Drive by removing stored tokens"""
    
    try:
        # Remove Google Drive tokens from user
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(
                google_drive_token=None,
                google_refresh_token=None,
                google_token_expiry=None
            )
        )
        await db.commit()
        
        return {"message": "Google Drive disconnected successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect Google Drive: {str(e)}"
        )


@router.get("/files", response_model=GoogleDriveFileList)
async def list_google_drive_files(
    file_type: Optional[str] = Query(None, description="Filter by file type: document, spreadsheet, presentation"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of files to return"),
    current_user: User = Depends(get_current_active_user)
):
    """List files from Google Drive"""
    
    # Check if user has Google Drive connected
    if not current_user.google_drive_token:
        raise HTTPException(
            status_code=400,
            detail="Google Drive not connected. Please connect your Google Drive account first."
        )
    
    try:
        # Get files from Google Drive
        files = await google_service.list_drive_files(
            access_token=current_user.google_drive_token,
            refresh_token=current_user.google_refresh_token,
            file_type=file_type,
            limit=limit
        )
        
        # Convert to Pydantic models
        drive_files = [GoogleDriveFile(**file_data) for file_data in files]
        
        return GoogleDriveFileList(
            files=drive_files,
            total_count=len(drive_files)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list Google Drive files: {str(e)}"
        )


@router.get("/files/{file_id}/content", response_model=GoogleDocumentContent)
async def get_google_document_content(
    file_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get content from a Google Document"""
    
    # Check if user has Google Drive connected
    if not current_user.google_drive_token:
        raise HTTPException(
            status_code=400,
            detail="Google Drive not connected. Please connect your Google Drive account first."
        )
    
    try:
        # Get document content
        document_data = await google_service.get_document_content(
            document_id=file_id,
            access_token=current_user.google_drive_token,
            refresh_token=current_user.google_refresh_token
        )
        
        return GoogleDocumentContent(**document_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Google Document content: {str(e)}"
        )


@router.post("/files/{file_id}/edit")
async def edit_google_doc(
    file_id: str,
    content: str,
    current_user: User = Depends(get_current_active_user)
):
    """Edit a Google Doc (placeholder for future implementation)"""
    
    # Check if user has Google Drive connected
    if not current_user.google_drive_token:
        raise HTTPException(
            status_code=400,
            detail="Google Drive not connected. Please connect your Google Drive account first."
        )
    
    # TODO: Implement Google Docs editing
    # This would involve using the Google Docs API to make batch updates
    
    return {
        "message": "Document editing will be implemented in the next phase",
        "file_id": file_id,
        "content_length": len(content)
    }
