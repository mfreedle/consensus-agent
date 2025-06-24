from app.database.connection import Base
from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, String)
from sqlalchemy.sql import func


class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # Local file path
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, etc.
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=True)
    
    # Google Drive integration
    google_drive_id = Column(String(100), nullable=True)
    google_drive_url = Column(String(500), nullable=True)
    
    # File processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(String(500), nullable=True)
    
    # Metadata
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
