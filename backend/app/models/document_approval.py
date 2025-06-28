import enum
from datetime import datetime

from app.database.connection import Base
from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Index, Integer, String, Text)
from sqlalchemy.orm import relationship


class ApprovalStatus(enum.Enum):
    """Status of a document approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    AUTO_APPROVED = "auto_approved"


class ChangeType(enum.Enum):
    """Type of change being proposed"""
    CONTENT_EDIT = "content_edit"
    STRUCTURE_CHANGE = "structure_change"
    FORMATTING = "formatting"
    ADDITION = "addition"
    DELETION = "deletion"
    REPLACEMENT = "replacement"


class DocumentApproval(Base):
    """Model for document approval requests"""
    __tablename__ = "document_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    
    # Approval details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    change_type = Column(Enum(ChangeType), nullable=False)
    
    # Content changes
    original_content = Column(Text, nullable=True)
    proposed_content = Column(Text, nullable=False)
    change_location = Column(String(500), nullable=True)  # Line numbers, sections, etc.
    change_metadata = Column(JSON, nullable=True)  # Additional metadata about the change
    
    # AI context
    ai_reasoning = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Approval status
    status = Column(Enum(ApprovalStatus, values_callable=lambda obj: [e.value for e in obj]), default=ApprovalStatus.PENDING, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    approved_by_user = Column(Boolean, default=False)
    
    # Expiration
    expires_at = Column(DateTime, nullable=False)
    
    # Version tracking
    version_before = Column(String(64), nullable=True)  # Hash of content before change
    version_after = Column(String(64), nullable=True)   # Hash of content after change
    
    # Application tracking
    is_applied = Column(Boolean, default=False)
    applied_at = Column(DateTime, nullable=True)
    application_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="document_approvals")
    file = relationship("File", back_populates="approvals")
    chat_session = relationship("ChatSession", back_populates="approvals")
    versions = relationship("DocumentVersion", back_populates="approval", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        Index("idx_file_status", "file_id", "status"),
        Index("idx_expires_at", "expires_at"),
        Index("idx_created_at", "created_at"),
    )


class DocumentVersion(Base):
    """Model for document version history"""
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    approval_id = Column(Integer, ForeignKey("document_approvals.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Version details
    version_number = Column(Integer, nullable=False)  # Incremental version number
    version_hash = Column(String(64), nullable=False, unique=True)  # Content hash
    content_snapshot = Column(Text, nullable=False)
    content_diff = Column(Text, nullable=True)
    
    # Change metadata
    change_summary = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    file_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    file = relationship("File", back_populates="versions")
    approval = relationship("DocumentApproval", back_populates="versions")
    user = relationship("User", back_populates="document_versions")
    
    # Indexes
    __table_args__ = (
        Index("idx_file_version", "file_id", "version_number"),
        Index("idx_version_hash", "version_hash"),
    )


class ApprovalTemplate(Base):
    """Model for auto-approval templates"""
    __tablename__ = "approval_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Template details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Matching criteria
    change_types = Column(JSON, nullable=False)  # List of ChangeType values
    file_patterns = Column(JSON, nullable=True)  # List of file patterns to match
    content_patterns = Column(JSON, nullable=True)  # List of content patterns
    
    # Auto-approval conditions
    max_confidence_required = Column(Float, default=0.8)  # Minimum confidence score
    max_change_size = Column(Integer, nullable=True)  # Maximum characters changed
    require_ai_reasoning = Column(Boolean, default=True)
    
    # Flags
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="approval_templates")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_active", "user_id", "is_active"),
    )
