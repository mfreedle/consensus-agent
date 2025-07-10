"""
Google Drive context integration for knowledge base
Allows LLMs to access Google Drive files as part of their context
"""

import logging
from typing import Dict, Optional

from app.google.service import GoogleDriveService
from app.models.user import User
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GoogleDriveFileContext(BaseModel):
    """Context information for a Google Drive file"""
    file_id: str
    title: str
    file_type: str  # document, spreadsheet, presentation
    content: str
    web_view_link: str
    last_modified: Optional[str] = None


class GoogleDriveContextManager:
    """Manages Google Drive files as part of the knowledge base context"""
    
    def __init__(self, google_service: GoogleDriveService):
        self.google_service = google_service
    
    def _get_user_tokens(self, user: User) -> tuple[Optional[str], Optional[str]]:
        """Get access and refresh tokens from user"""
        access_token = getattr(user, 'google_drive_token', None)
        refresh_token = getattr(user, 'google_refresh_token', None)
        return access_token, refresh_token
    
    async def get_google_drive_context(self, user: User, limit: int = 10) -> str:
        """Get Google Drive files context for inclusion in LLM prompts"""
        
        access_token, refresh_token = self._get_user_tokens(user)
        
        if not access_token:
            return ""
        
        try:
            # Get list of recent files
            files = await self.google_service.list_drive_files(
                access_token=access_token,
                refresh_token=refresh_token,
                limit=limit
            )
            
            if not files:
                return ""
            
            # Build context for each file
            file_contexts = []
            total_context_length = 0
            max_context_length = 20000  # Limit to prevent context overflow
            
            for file_info in files:
                if total_context_length >= max_context_length:
                    break
                
                try:
                    file_context = await self._get_file_context(
                        file_info, access_token, refresh_token
                    )
                    
                    if file_context:
                        context_entry = f"\n--- Google Drive: {file_context.title} ({file_context.file_type}) ---\n"
                        context_entry += f"File ID: {file_context.file_id}\n"
                        context_entry += f"Link: {file_context.web_view_link}\n"
                        context_entry += f"Content: {file_context.content[:3000]}"
                        
                        if len(file_context.content) > 3000:
                            context_entry += "\n... (content truncated)"
                        
                        context_entry += "\n"
                        
                        if total_context_length + len(context_entry) > max_context_length:
                            break
                        
                        file_contexts.append(context_entry)
                        total_context_length += len(context_entry)
                        
                except Exception as e:
                    logger.warning(f"Error getting context for file {file_info.get('id', 'unknown')}: {e}")
                    continue
            
            if file_contexts:
                context = "\n\nGoogle Drive Files (available for reference and editing):\n"
                context += "".join(file_contexts)
                context += "\nNote: You can read, edit, or create Google Drive files using available functions.\n"
                return context
            
        except Exception as e:
            logger.error(f"Error getting Google Drive context: {e}")
        
        return ""
    
    async def _get_file_context(
        self, 
        file_info: Dict, 
        access_token: str, 
        refresh_token: Optional[str]
    ) -> Optional[GoogleDriveFileContext]:
        """Get context for a specific Google Drive file"""
        
        file_id = file_info.get("id")
        file_type = file_info.get("type")
        title = file_info.get("name", "Untitled")
        
        if not file_id or not file_type:
            return None
        
        try:
            content = ""
            
            if file_type == "document":
                doc_data = await self.google_service.get_document_content(
                    document_id=file_id,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
                content = doc_data.get("content", "")
                
            elif file_type == "spreadsheet":
                sheet_data = await self.google_service.get_spreadsheet_content(
                    spreadsheet_id=file_id,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
                # Convert sheet data to readable format
                sheets = sheet_data.get("sheets", {})
                content_parts = []
                for sheet_name, rows in sheets.items():
                    content_parts.append(f"Sheet: {sheet_name}")
                    for i, row in enumerate(rows[:10]):  # Limit to first 10 rows
                        content_parts.append(f"Row {i+1}: {', '.join(str(cell) for cell in row)}")
                    if len(rows) > 10:
                        content_parts.append(f"... ({len(rows) - 10} more rows)")
                content = "\n".join(content_parts)
                
            elif file_type == "presentation":
                pres_data = await self.google_service.get_presentation_content(
                    presentation_id=file_id,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
                # Convert slide data to readable format
                slides = pres_data.get("slides", [])
                content_parts = []
                for i, slide in enumerate(slides[:5]):  # Limit to first 5 slides
                    slide_id = slide.get("slide_id", f"slide_{i+1}")
                    text_content = slide.get("text_content", [])
                    content_parts.append(f"Slide {i+1} ({slide_id}): {' '.join(text_content)}")
                if len(slides) > 5:
                    content_parts.append(f"... ({len(slides) - 5} more slides)")
                content = "\n".join(content_parts)
            
            if content:
                return GoogleDriveFileContext(
                    file_id=file_id,
                    title=title,
                    file_type=file_type,
                    content=content,
                    web_view_link=file_info.get("web_view_link", ""),
                    last_modified=file_info.get("modified_time")
                )
                
        except Exception as e:
            logger.error(f"Error reading file {file_id}: {e}")
        
        return None
    
    async def get_google_drive_files_summary(self, user: User) -> Dict:
        """Get summary of user's Google Drive files"""
        
        access_token, refresh_token = self._get_user_tokens(user)
        
        if not access_token:
            return {
                "connected": False,
                "total_files": 0,
                "by_type": {},
                "message": "Google Drive not connected"
            }
        
        try:
            # Get all files
            files = await self.google_service.list_drive_files(
                access_token=access_token,
                refresh_token=refresh_token,
                limit=100
            )
            
            # Count by type
            by_type = {}
            for file_info in files:
                file_type = file_info.get("type", "unknown")
                by_type[file_type] = by_type.get(file_type, 0) + 1
            
            return {
                "connected": True,
                "total_files": len(files),
                "by_type": by_type,
                "message": f"Found {len(files)} Google Drive files"
            }
            
        except Exception as e:
            logger.error(f"Error getting Google Drive files summary: {e}")
            return {
                "connected": False,
                "total_files": 0,
                "by_type": {},
                "message": f"Error accessing Google Drive: {str(e)}"
            }
