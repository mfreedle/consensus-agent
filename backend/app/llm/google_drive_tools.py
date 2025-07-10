"""
Google Drive tools for LLM integration
Allows LLMs to read, edit, and create Google Drive files
"""

import logging
from typing import Any, Dict, List, Optional

from app.google.service import GoogleDriveService
from app.models.user import User
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GoogleDriveFunction(BaseModel):
    """Base class for Google Drive function calls"""
    name: str
    description: str
    parameters: Dict[str, Any]


class GoogleDriveToolResult(BaseModel):
    """Result from a Google Drive tool operation"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GoogleDriveTools:
    """Google Drive tools for LLM function calling"""
    
    def __init__(self, google_service: GoogleDriveService):
        self.google_service = google_service
    
    def _get_user_tokens(self, user: User) -> tuple[Optional[str], Optional[str]]:
        """Get access and refresh tokens from user, handling SQLAlchemy column types"""
        access_token = getattr(user, 'google_drive_token', None)
        refresh_token = getattr(user, 'google_refresh_token', None)
        return access_token, refresh_token
    
    def get_available_functions(self) -> List[GoogleDriveFunction]:
        """Get list of available Google Drive functions for LLM"""
        return [
            GoogleDriveFunction(
                name="list_google_drive_files",
                description="List files from user's Google Drive. Use this to see what files are available before reading or editing them.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_type": {
                            "type": "string",
                            "enum": ["document", "spreadsheet", "presentation", "all"],
                            "description": "Filter files by type (document, spreadsheet, presentation, or all)"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 20,
                            "description": "Maximum number of files to return"
                        }
                    }
                }
            ),
            GoogleDriveFunction(
                name="read_google_document",
                description="Read content from a Google Document. Use this to get the current content before editing.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID of the document to read"
                        }
                    },
                    "required": ["file_id"]
                }
            ),
            GoogleDriveFunction(
                name="read_google_spreadsheet",
                description="Read content from a Google Spreadsheet. Use this to see the current data before editing.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID of the spreadsheet to read"
                        }
                    },
                    "required": ["file_id"]
                }
            ),
            GoogleDriveFunction(
                name="read_google_presentation",
                description="Read content from a Google Slides presentation. Use this to see the current slides before editing.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID of the presentation to read"
                        }
                    },
                    "required": ["file_id"]
                }
            ),
            GoogleDriveFunction(
                name="edit_google_document",
                description="Edit content in a Google Document. This will replace ALL content in the document.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID of the document to edit"
                        },
                        "content": {
                            "type": "string",
                            "description": "The new content for the document. This will replace all existing content."
                        }
                    },
                    "required": ["file_id", "content"]
                }
            ),
            GoogleDriveFunction(
                name="edit_google_spreadsheet",
                description="Edit data in a Google Spreadsheet. Specify the sheet name, range, and new values.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID of the spreadsheet to edit"
                        },
                        "sheet_name": {
                            "type": "string",
                            "description": "The name of the sheet to edit (e.g., 'Sheet1')"
                        },
                        "range_name": {
                            "type": "string",
                            "description": "The range to update (e.g., 'A1:C10')"
                        },
                        "values": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "description": "2D array of values to insert. Each sub-array represents a row."
                        }
                    },
                    "required": ["file_id", "sheet_name", "range_name", "values"]
                }
            ),
            GoogleDriveFunction(
                name="create_google_document",
                description="Create a new Google Document with the specified title and content.",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title for the new document"
                        },
                        "content": {
                            "type": "string",
                            "description": "Initial content for the document"
                        }
                    },
                    "required": ["title", "content"]
                }
            ),
            GoogleDriveFunction(
                name="create_google_spreadsheet",
                description="Create a new Google Spreadsheet with the specified title.",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title for the new spreadsheet"
                        }
                    },
                    "required": ["title"]
                }
            ),
            GoogleDriveFunction(
                name="create_google_presentation",
                description="Create a new Google Slides presentation with the specified title.",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title for the new presentation"
                        }
                    },
                    "required": ["title"]
                }
            ),
            GoogleDriveFunction(
                name="add_slide_to_presentation",
                description="Add a new slide with text to an existing Google Slides presentation.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID of the presentation"
                        },
                        "title": {
                            "type": "string",
                            "description": "Title for the new slide"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content text for the new slide"
                        }
                    },
                    "required": ["file_id", "title", "content"]
                }
            )
        ]
    
    async def execute_function(self, function_name: str, parameters: Dict[str, Any], user: User) -> GoogleDriveToolResult:
        """Execute a Google Drive function with the given parameters"""
        
        # Check if user has Google Drive connected
        access_token, refresh_token = self._get_user_tokens(user)
        
        if not access_token:
            return GoogleDriveToolResult(
                success=False,
                message="Google Drive not connected. Please connect your Google Drive account first.",
                error="NO_GOOGLE_DRIVE_TOKEN"
            )
        
        try:
            if function_name == "list_google_drive_files":
                return await self._list_files(parameters, access_token, refresh_token)
            elif function_name == "read_google_document":
                return await self._read_document(parameters, access_token, refresh_token)
            elif function_name == "read_google_spreadsheet":
                return await self._read_spreadsheet(parameters, access_token, refresh_token)
            elif function_name == "read_google_presentation":
                return await self._read_presentation(parameters, access_token, refresh_token)
            elif function_name == "edit_google_document":
                return await self._edit_document(parameters, access_token, refresh_token)
            elif function_name == "edit_google_spreadsheet":
                return await self._edit_spreadsheet(parameters, access_token, refresh_token)
            elif function_name == "create_google_document":
                return await self._create_document(parameters, access_token, refresh_token)
            elif function_name == "create_google_spreadsheet":
                return await self._create_spreadsheet(parameters, access_token, refresh_token)
            elif function_name == "create_google_presentation":
                return await self._create_presentation(parameters, access_token, refresh_token)
            elif function_name == "add_slide_to_presentation":
                return await self._add_slide(parameters, access_token, refresh_token)
            else:
                return GoogleDriveToolResult(
                    success=False,
                    message=f"Unknown function: {function_name}",
                    error="UNKNOWN_FUNCTION"
                )
        
        except Exception as e:
            logger.error(f"Error executing Google Drive function {function_name}: {e}")
            return GoogleDriveToolResult(
                success=False,
                message=f"Error executing {function_name}: {str(e)}",
                error="EXECUTION_ERROR"
            )
    
    async def _list_files(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """List Google Drive files"""
        file_type = parameters.get("file_type", "all")
        limit = parameters.get("limit", 20)
        
        files = await self.google_service.list_drive_files(
            access_token=access_token,
            refresh_token=refresh_token,
            file_type=file_type if file_type != "all" else None,
            limit=limit
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Found {len(files)} files",
            data={
                "files": files,
                "count": len(files),
                "file_type": file_type
            }
        )
    
    async def _read_document(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Read Google Document content"""
        file_id = parameters["file_id"]
        
        document = await self.google_service.get_document_content(
            document_id=file_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Successfully read document: {document['title']}",
            data=document
        )
    
    async def _read_spreadsheet(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Read Google Spreadsheet content"""
        file_id = parameters["file_id"]
        
        spreadsheet = await self.google_service.get_spreadsheet_content(
            spreadsheet_id=file_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Successfully read spreadsheet: {spreadsheet['title']}",
            data=spreadsheet
        )
    
    async def _read_presentation(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Read Google Presentation content"""
        file_id = parameters["file_id"]
        
        presentation = await self.google_service.get_presentation_content(
            presentation_id=file_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Successfully read presentation: {presentation['title']}",
            data=presentation
        )
    
    async def _edit_document(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Edit Google Document content"""
        file_id = parameters["file_id"]
        content = parameters["content"]
        
        await self.google_service.edit_document_content(
            document_id=file_id,
            access_token=access_token,
            new_content=content,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message="Successfully edited document",
            data={
                "document_id": file_id,
                "web_view_link": f"https://docs.google.com/document/d/{file_id}/edit"
            }
        )
    
    async def _edit_spreadsheet(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Edit Google Spreadsheet content"""
        file_id = parameters["file_id"]
        sheet_name = parameters["sheet_name"]
        range_name = parameters["range_name"]
        values = parameters["values"]
        
        await self.google_service.edit_spreadsheet_content(
            spreadsheet_id=file_id,
            access_token=access_token,
            sheet_name=sheet_name,
            range_name=range_name,
            values=values,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Successfully edited spreadsheet range {sheet_name}!{range_name}",
            data={
                "spreadsheet_id": file_id,
                "updated_range": f"{sheet_name}!{range_name}",
                "web_view_link": f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
            }
        )
    
    async def _create_document(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Create new Google Document"""
        title = parameters["title"]
        content = parameters["content"]
        
        result = await self.google_service.create_document(
            access_token=access_token,
            title=title,
            content=content,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Successfully created document: {title}",
            data=result
        )
    
    async def _create_spreadsheet(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Create new Google Spreadsheet"""
        title = parameters["title"]
        
        result = await self.google_service.create_spreadsheet(
            access_token=access_token,
            title=title,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Successfully created spreadsheet: {title}",
            data=result
        )
    
    async def _create_presentation(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Create new Google Presentation"""
        title = parameters["title"]
        
        result = await self.google_service.create_presentation(
            access_token=access_token,
            title=title,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Successfully created presentation: {title}",
            data=result
        )
    
    async def _add_slide(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Add slide to Google Presentation"""
        file_id = parameters["file_id"]
        title = parameters["title"]
        content = parameters["content"]
        
        await self.google_service.add_slide_with_text(
            presentation_id=file_id,
            access_token=access_token,
            title=title,
            content=content,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Successfully added slide: {title}",
            data={
                "presentation_id": file_id,
                "slide_title": title,
                "web_view_link": f"https://docs.google.com/presentation/d/{file_id}/edit"
            }
        )
