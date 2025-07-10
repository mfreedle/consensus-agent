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
                            "type": ["string", "null"],
                            "enum": ["document", "spreadsheet", "presentation", "all", None],
                            "description": "Filter files by type (document, spreadsheet, presentation, or all). Pass null for all files."
                        },
                        "limit": {
                            "type": ["integer", "null"],
                            "minimum": 1,
                            "maximum": 50,
                            "description": "Maximum number of files to return. Pass null for default (20)."
                        }
                    },
                    "required": ["file_type", "limit"],
                    "additionalProperties": False
                }
            ),
            GoogleDriveFunction(
                name="search_google_drive_files",
                description="Search for files in Google Drive by name or content. This can find files in subfolders and search within document content.",
                parameters={
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "The search term to look for in file names or content"
                        },
                        "file_type": {
                            "type": ["string", "null"],
                            "enum": ["document", "spreadsheet", "presentation", "folder", "all", None],
                            "description": "Filter search results by file type. Pass null for all files."
                        },
                        "limit": {
                            "type": ["integer", "null"],
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of search results to return. Pass null for default (25)."
                        }
                    },
                    "required": ["search_query", "file_type", "limit"],
                    "additionalProperties": False
                }
            ),
            GoogleDriveFunction(
                name="list_folder_contents",
                description="List all files and subfolders within a specific Google Drive folder. Use this to explore folder contents.",
                parameters={
                    "type": "object",
                    "properties": {
                        "folder_id": {
                            "type": "string",
                            "description": "The Google Drive folder ID to list contents of"
                        },
                        "file_type": {
                            "type": ["string", "null"],
                            "enum": ["document", "spreadsheet", "presentation", "folder", "all", None],
                            "description": "Filter contents by file type. Pass null for all files."
                        },
                        "limit": {
                            "type": ["integer", "null"],
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of items to return. Pass null for default (50)."
                        }
                    },
                    "required": ["folder_id", "file_type", "limit"],
                    "additionalProperties": False
                }
            ),
            GoogleDriveFunction(
                name="find_folder_by_name",
                description="Find a folder in Google Drive by its name. Use this to locate folders before listing their contents.",
                parameters={
                    "type": "object",
                    "properties": {
                        "folder_name": {
                            "type": "string",
                            "description": "The name of the folder to find"
                        }
                    },
                    "required": ["folder_name"],
                    "additionalProperties": False
                }
            ),
            GoogleDriveFunction(
                name="get_file_path",
                description="Get the full path/location of a file in Google Drive to understand its folder structure.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID to get the path for"
                        }
                    },
                    "required": ["file_id"],
                    "additionalProperties": False
                }
            ),
            GoogleDriveFunction(
                name="list_all_files_with_paths",
                description="List all files with their full folder paths. Use this to get a comprehensive view of file organization.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_type": {
                            "type": ["string", "null"],
                            "enum": ["document", "spreadsheet", "presentation", "all", None],
                            "description": "Filter files by type. Pass null for all files."
                        },
                        "limit": {
                            "type": ["integer", "null"],
                            "minimum": 1,
                            "maximum": 200,
                            "description": "Maximum number of files to return. Pass null for default (100)."
                        }
                    },
                    "required": ["file_type", "limit"],
                    "additionalProperties": False
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
                    "required": ["file_id"],
                    "additionalProperties": False
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
                    "required": ["file_id"],
                    "additionalProperties": False
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
                    "required": ["file_id"],
                    "additionalProperties": False
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
                    "required": ["file_id", "content"],
                    "additionalProperties": False
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
                    "required": ["file_id", "sheet_name", "range_name", "values"],
                    "additionalProperties": False
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
                    "required": ["title", "content"],
                    "additionalProperties": False
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
                    "required": ["title"],
                    "additionalProperties": False
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
                    "required": ["title"],
                    "additionalProperties": False
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
                    "required": ["file_id", "title", "content"],
                    "additionalProperties": False
                }
            ),
            GoogleDriveFunction(
                name="copy_google_drive_file",
                description="Copy a file in Google Drive to a new location with optional renaming. Use this to make copies of files.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID to copy"
                        },
                        "new_name": {
                            "type": ["string", "null"],
                            "description": "Optional new name for the copied file. Pass null to use 'Copy of [original name]'"
                        },
                        "target_folder_id": {
                            "type": ["string", "null"],
                            "description": "Optional folder ID to copy the file to. Pass null for current folder or use 'root' for main Drive folder"
                        }
                    },
                    "required": ["file_id", "new_name", "target_folder_id"],
                    "additionalProperties": False
                }
            ),
            GoogleDriveFunction(
                name="move_google_drive_file",
                description="Move a file from one folder to another in Google Drive. Use this to relocate files.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID to move"
                        },
                        "target_folder_id": {
                            "type": "string",
                            "description": "The folder ID to move the file to. Use 'root' for main Drive folder or get folder ID from find_folder_by_name"
                        }
                    },
                    "required": ["file_id", "target_folder_id"],
                    "additionalProperties": False
                }
            ),
            GoogleDriveFunction(
                name="delete_google_drive_file",
                description="Delete a file from Google Drive (moves to trash). Use this to remove unwanted files.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The Google Drive file ID to delete"
                        }
                    },
                    "required": ["file_id"],
                    "additionalProperties": False
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
            elif function_name == "search_google_drive_files":
                return await self._search_files(parameters, access_token, refresh_token)
            elif function_name == "list_folder_contents":
                return await self._list_folder_contents(parameters, access_token, refresh_token)
            elif function_name == "find_folder_by_name":
                return await self._find_folder_by_name(parameters, access_token, refresh_token)
            elif function_name == "get_file_path":
                return await self._get_file_path(parameters, access_token, refresh_token)
            elif function_name == "list_all_files_with_paths":
                return await self._list_all_files_with_paths(parameters, access_token, refresh_token)
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
            elif function_name == "copy_google_drive_file":
                return await self._copy_file(parameters, access_token, refresh_token)
            elif function_name == "move_google_drive_file":
                return await self._move_file(parameters, access_token, refresh_token)
            elif function_name == "delete_google_drive_file":
                return await self._delete_file(parameters, access_token, refresh_token)
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
        file_type = parameters.get("file_type")
        limit = parameters.get("limit")
        
        # Handle null values from strict mode
        if file_type is None:
            file_type = "all"
        if limit is None:
            limit = 20
        
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

    async def _search_files(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Search for files in Google Drive"""
        search_query = parameters.get("search_query", "")
        file_type = parameters.get("file_type")
        limit = parameters.get("limit")
        
        # Handle null values from strict mode
        if file_type is None:
            file_type = "all"
        if limit is None:
            limit = 25
        
        if not search_query:
            return GoogleDriveToolResult(
                success=False,
                message="Search query is required",
                error="MISSING_SEARCH_QUERY"
            )
        
        files = await self.google_service.search_drive_files(
            access_token=access_token,
            search_query=search_query,
            refresh_token=refresh_token,
            file_type=file_type,
            limit=limit
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Found {len(files)} files matching '{search_query}'",
            data={"files": files, "search_query": search_query, "total_count": len(files)}
        )

    async def _list_folder_contents(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """List contents of a specific folder"""
        folder_id = parameters.get("folder_id", "")
        file_type = parameters.get("file_type")
        limit = parameters.get("limit")
        
        # Handle null values from strict mode
        if file_type is None:
            file_type = "all"
        if limit is None:
            limit = 50
        
        if not folder_id:
            return GoogleDriveToolResult(
                success=False,
                message="Folder ID is required",
                error="MISSING_FOLDER_ID"
            )
        
        files = await self.google_service.list_folder_contents(
            folder_id=folder_id,
            access_token=access_token,
            refresh_token=refresh_token,
            file_type=file_type,
            limit=limit
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Found {len(files)} items in folder",
            data={"files": files, "folder_id": folder_id, "total_count": len(files)}
        )

    async def _find_folder_by_name(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Find a folder by name"""
        folder_name = parameters.get("folder_name", "")
        
        if not folder_name:
            return GoogleDriveToolResult(
                success=False,
                message="Folder name is required",
                error="MISSING_FOLDER_NAME"
            )
        
        folder = await self.google_service.get_folder_by_name(
            folder_name=folder_name,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        if folder:
            return GoogleDriveToolResult(
                success=True,
                message=f"Found folder: {folder_name}",
                data={"folder": folder}
            )
        else:
            return GoogleDriveToolResult(
                success=False,
                message=f"Folder '{folder_name}' not found",
                error="FOLDER_NOT_FOUND"
            )

    async def _get_file_path(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Get the full path of a file"""
        file_id = parameters.get("file_id", "")
        
        if not file_id:
            return GoogleDriveToolResult(
                success=False,
                message="File ID is required",
                error="MISSING_FILE_ID"
            )
        
        path = await self.google_service.get_file_path(
            file_id=file_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message="File path retrieved",
            data={"file_id": file_id, "path": path}
        )

    async def _list_all_files_with_paths(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """List all files with their full paths"""
        file_type = parameters.get("file_type")
        limit = parameters.get("limit")
        
        # Handle null values from strict mode
        if file_type is None:
            file_type = "all"
        if limit is None:
            limit = 100
        
        files = await self.google_service.list_all_files_with_paths(
            access_token=access_token,
            refresh_token=refresh_token,
            file_type=file_type,
            limit=limit
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"Retrieved {len(files)} files with paths",
            data={"files": files, "total_count": len(files)}
        )

    async def _copy_file(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Copy a file in Google Drive"""
        file_id = parameters.get("file_id", "")
        new_name = parameters.get("new_name")
        target_folder_id = parameters.get("target_folder_id")
        
        if not file_id:
            return GoogleDriveToolResult(
                success=False,
                message="File ID is required",
                error="MISSING_FILE_ID"
            )
        
        # Handle special case for root folder
        if target_folder_id == "root":
            root_id = await self.google_service.get_root_folder_id(
                access_token=access_token,
                refresh_token=refresh_token
            )
            target_folder_id = root_id
        
        copied_file = await self.google_service.copy_file(
            file_id=file_id,
            access_token=access_token,
            new_name=new_name,
            target_folder_id=target_folder_id,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"File copied successfully: {copied_file['name']}",
            data={"copied_file": copied_file}
        )

    async def _move_file(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Move a file in Google Drive"""
        file_id = parameters.get("file_id", "")
        target_folder_id = parameters.get("target_folder_id", "")
        
        if not file_id:
            return GoogleDriveToolResult(
                success=False,
                message="File ID is required",
                error="MISSING_FILE_ID"
            )
        
        if not target_folder_id:
            return GoogleDriveToolResult(
                success=False,
                message="Target folder ID is required",
                error="MISSING_TARGET_FOLDER_ID"
            )
        
        # Handle special case for root folder
        if target_folder_id == "root":
            root_id = await self.google_service.get_root_folder_id(
                access_token=access_token,
                refresh_token=refresh_token
            )
            target_folder_id = root_id
        
        moved_file = await self.google_service.move_file(
            file_id=file_id,
            access_token=access_token,
            target_folder_id=target_folder_id,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=f"File moved successfully: {moved_file['name']}",
            data={"moved_file": moved_file}
        )

    async def _delete_file(self, parameters: Dict[str, Any], access_token: str, refresh_token: Optional[str]) -> GoogleDriveToolResult:
        """Delete a file in Google Drive"""
        file_id = parameters.get("file_id", "")
        
        if not file_id:
            return GoogleDriveToolResult(
                success=False,
                message="File ID is required",
                error="MISSING_FILE_ID"
            )
        
        result = await self.google_service.delete_file(
            file_id=file_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return GoogleDriveToolResult(
            success=True,
            message=result["message"],
            data=result
        )
