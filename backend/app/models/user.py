from app.database.connection import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Google Drive integration
    google_drive_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expiry = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document_approvals = relationship("DocumentApproval", back_populates="user")
    document_versions = relationship("DocumentVersion", back_populates="user")
    approval_templates = relationship("ApprovalTemplate", back_populates="user")
