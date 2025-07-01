import os
from pathlib import Path

import aiofiles
from app.auth.dependencies import get_current_active_user
from app.config import settings
from app.database.connection import get_db
from app.files.processor import extract_text_from_file
from app.models.file import File
from app.models.user import User
from fastapi import APIRouter, Depends
from fastapi import File as FastAPIFile
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
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
    
    # Generate unique filename to avoid conflicts
    import uuid
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file to disk
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Save file metadata to database
    db_file = File(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_type=file_extension.lower().lstrip('.'),
        file_size=file.size,
        mime_type=file.content_type,
        is_processed=False
    )
    
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    
    # Process file content in the background
    try:
        success, extracted_text, error_message = await extract_text_from_file(
            str(file_path), 
            file_extension.lower().lstrip('.')
        )
        
        if success:
            db_file.extracted_text = extracted_text
            db_file.is_processed = True
        else:
            db_file.processing_error = error_message
            db_file.is_processed = False
            
        await db.commit()
        
    except Exception as e:
        # Don't fail the upload if processing fails
        db_file.processing_error = f"Processing failed: {str(e)}"
        db_file.is_processed = False
        await db.commit()
    
    return {
        "id": db_file.id,
        "message": "File uploaded successfully",
        "filename": file.filename,
        "size": file.size,
        "is_processed": db_file.is_processed
    }

@router.get("")
async def list_files(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's files"""
    
    # Get files from database
    result = await db.execute(
        select(File).where(File.user_id == current_user.id).order_by(File.uploaded_at.desc())
    )
    files = result.scalars().all()
    
    # Convert to response format
    files_data = []
    for file in files:
        files_data.append({
            "id": str(file.id),
            "filename": file.original_filename,
            "file_type": file.file_type,
            "file_size": file.file_size,
            "mime_type": file.mime_type,
            "is_processed": file.is_processed,
            "processing_error": file.processing_error,
            "google_drive_id": file.google_drive_id,
            "uploaded_at": file.uploaded_at.isoformat() if file.uploaded_at else None,
            "updated_at": file.updated_at.isoformat() if file.updated_at else None
        })
    
    return {"files": files_data}

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file"""
    
    print(f"DEBUG: Delete request received for file ID: {file_id} by user: {current_user.username}")
    
    # Get file from database
    result = await db.execute(
        select(File).where(File.id == int(file_id), File.user_id == current_user.id)
    )
    file = result.scalar_one_or_none()
    
    if not file:
        print(f"DEBUG: File not found - ID: {file_id}, User ID: {current_user.id}")
        raise HTTPException(status_code=404, detail="File not found")
    
    print(f"DEBUG: File found - {file.original_filename}, deleting...")
    
    # Delete file from disk if it exists
    if file.file_path and os.path.exists(file.file_path):
        try:
            os.remove(file.file_path)
            print(f"DEBUG: File deleted from disk: {file.file_path}")
        except OSError as e:
            print(f"DEBUG: Error deleting file from disk: {e}")
            pass  # File already deleted or permission issue
    
    # Delete from database
    await db.delete(file)
    await db.commit()
    
    print("DEBUG: File deleted successfully from database")
    return {"message": "File deleted successfully"}

@router.get("/{file_id}/content")
async def get_file_content(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get extracted text content from a file"""
    
    # Get file from database
    result = await db.execute(
        select(File).where(File.id == int(file_id), File.user_id == current_user.id)
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "id": file.id,
        "filename": file.original_filename,
        "is_processed": file.is_processed,
        "processing_error": file.processing_error,
        "extracted_text": file.extracted_text[:1000] + "..." if file.extracted_text and len(file.extracted_text) > 1000 else file.extracted_text,
        "text_length": len(file.extracted_text) if file.extracted_text else 0
    }
