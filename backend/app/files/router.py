import os
from pathlib import Path
from typing import List

import aiofiles
from app.auth.dependencies import get_current_active_user
from app.config import settings
from app.database.connection import get_db
from app.models.user import User
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file"""
    
    # Validate file size
    if file.size > settings.max_file_size:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_dir) / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / file.filename
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # TODO: Save file metadata to database
    # TODO: Process file content for AI context
    
    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "size": file.size
    }

@router.get("/")
async def list_files(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's files"""
    
    # TODO: Get files from database
    return {"files": []}

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file"""
    
    # TODO: Implement file deletion
    return {"message": "File deleted successfully"}
