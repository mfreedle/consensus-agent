from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ChangeType(str, Enum):
    CONTENT_EDIT = "content_edit"
    CONTENT_APPEND = "content_append"
    CONTENT_INSERT = "content_insert"
    CONTENT_DELETE = "content_delete"
    FORMATTING_CHANGE = "formatting_change"
    METADATA_UPDATE = "metadata_update"


# Request schemas
class CreateApprovalRequest(BaseModel):
    file_id: int
    chat_session_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    change_type: ChangeType
    original_content: Optional[str] = None
    proposed_content: str
    change_location: Optional[Dict] = None
    change_metadata: Optional[Dict] = None
    ai_reasoning: Optional[str] = None
    confidence_score: Optional[int] = Field(None, ge=1, le=100)
    expires_in_hours: Optional[int] = Field(24, ge=1, le=168)  # Max 1 week


class ApprovalDecisionRequest(BaseModel):
    approval_id: Optional[int] = None  # Optional since it's provided via URL path
    decision: ApprovalStatus = Field(..., description="Must be 'approved' or 'rejected'")
    reason: Optional[str] = None


class BulkApprovalRequest(BaseModel):
    approval_ids: List[int]
    decision: ApprovalStatus = Field(..., description="Must be 'approved' or 'rejected'")
    reason: Optional[str] = None


class ApprovalTemplateCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    change_type: ChangeType
    auto_approve: bool = False
    requires_manual_review: bool = True
    expiration_hours: int = Field(24, ge=1, le=168)
    file_type_filter: Optional[str] = None
    confidence_threshold: int = Field(80, ge=1, le=100)


class ApprovalTemplateUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    auto_approve: Optional[bool] = None
    requires_manual_review: Optional[bool] = None
    expiration_hours: Optional[int] = Field(None, ge=1, le=168)
    file_type_filter: Optional[str] = None
    confidence_threshold: Optional[int] = Field(None, ge=1, le=100)
    is_active: Optional[bool] = None


# Response schemas
class ChangeLocationResponse(BaseModel):
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    section: Optional[str] = None


class DocumentApprovalResponse(BaseModel):
    id: int
    file_id: int
    chat_session_id: Optional[int]
    title: str
    description: Optional[str]
    change_type: ChangeType
    original_content: Optional[str]
    proposed_content: str
    change_location: Optional[Dict]
    change_metadata: Optional[Dict]
    ai_reasoning: Optional[str]
    confidence_score: Optional[int]
    status: ApprovalStatus
    approved_at: Optional[datetime]
    approved_by_user: bool
    expires_at: Optional[datetime]
    version_before: Optional[str]
    version_after: Optional[str]
    is_applied: bool
    applied_at: Optional[datetime]
    application_error: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    file_name: Optional[str] = None
    chat_session_title: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentVersionResponse(BaseModel):
    id: int
    file_id: int
    version_hash: str
    version_number: int
    content_snapshot: str
    content_diff: Optional[str]
    change_summary: Optional[str]
    file_size: Optional[int]
    file_metadata: Optional[Dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApprovalTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    change_type: ChangeType
    auto_approve: bool
    requires_manual_review: bool
    expiration_hours: int
    file_type_filter: Optional[str]
    confidence_threshold: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ApprovalSummaryResponse(BaseModel):
    total_pending: int
    total_approved: int
    total_rejected: int
    total_expired: int
    recent_approvals: List[DocumentApprovalResponse]


class VersionHistoryResponse(BaseModel):
    file_id: int
    file_name: str
    current_version: int
    total_versions: int
    versions: List[DocumentVersionResponse]


# Diff and Preview schemas
class ContentDiffResponse(BaseModel):
    original_lines: List[str]
    proposed_lines: List[str]
    diff_html: str
    diff_text: str
    change_summary: str
    lines_added: int
    lines_removed: int
    lines_modified: int


class ApprovalPreviewResponse(BaseModel):
    approval: DocumentApprovalResponse
    content_diff: ContentDiffResponse
    impact_analysis: Dict
    recommendations: List[str]
