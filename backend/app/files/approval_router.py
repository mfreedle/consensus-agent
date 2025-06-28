from typing import List

from app.auth.dependencies import get_current_active_user
from app.database.connection import get_db
from app.files.approval_service import DocumentApprovalService
from app.models.user import User
from app.schemas.document_approval import (ApprovalDecisionRequest,
                                           ApprovalStatus,
                                           ApprovalSummaryResponse,
                                           ApprovalTemplateCreateRequest,
                                           ApprovalTemplateResponse,
                                           ApprovalTemplateUpdateRequest,
                                           BulkApprovalRequest,
                                           ContentDiffResponse,
                                           CreateApprovalRequest,
                                           DocumentApprovalResponse,
                                           VersionHistoryResponse)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/approvals", response_model=DocumentApprovalResponse)
async def create_approval_request(
    request: CreateApprovalRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new document approval request"""
    
    try:
        service = DocumentApprovalService(db)
        approval = await service.create_approval_request(current_user.id, request)
        
        return DocumentApprovalResponse(
            id=approval.id,
            file_id=approval.file_id,
            chat_session_id=approval.chat_session_id,
            title=approval.title,
            description=approval.description,
            change_type=approval.change_type,
            original_content=approval.original_content,
            proposed_content=approval.proposed_content,
            change_location=approval.change_location,
            change_metadata=approval.change_metadata,
            ai_reasoning=approval.ai_reasoning,
            confidence_score=approval.confidence_score,
            status=approval.status,
            approved_at=approval.approved_at,
            approved_by_user=approval.approved_by_user,
            expires_at=approval.expires_at,
            version_before=approval.version_before,
            version_after=approval.version_after,
            is_applied=approval.is_applied,
            applied_at=approval.applied_at,
            application_error=approval.application_error,
            created_at=approval.created_at,
            updated_at=approval.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating approval request: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create approval request: {str(e)}")


@router.get("/approvals/pending", response_model=List[DocumentApprovalResponse])
async def get_pending_approvals(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pending approval requests for the current user"""
    
    service = DocumentApprovalService(db)
    approvals = await service.get_pending_approvals(current_user.id, limit)
    
    return [
        DocumentApprovalResponse(
            id=approval.id,
            file_id=approval.file_id,
            chat_session_id=approval.chat_session_id,
            title=approval.title,
            description=approval.description,
            change_type=approval.change_type,
            original_content=approval.original_content,
            proposed_content=approval.proposed_content,
            change_location=approval.change_location,
            change_metadata=approval.change_metadata,
            ai_reasoning=approval.ai_reasoning,
            confidence_score=approval.confidence_score,
            status=approval.status,
            approved_at=approval.approved_at,
            approved_by_user=approval.approved_by_user,
            expires_at=approval.expires_at,
            version_before=approval.version_before,
            version_after=approval.version_after,
            is_applied=approval.is_applied,
            applied_at=approval.applied_at,
            application_error=approval.application_error,
            created_at=approval.created_at,
            updated_at=approval.updated_at,
            file_name=approval.file.original_filename if approval.file else None
        )
        for approval in approvals
    ]


@router.get("/approvals/history", response_model=List[DocumentApprovalResponse])
async def get_approval_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get approval history for the current user"""
    
    service = DocumentApprovalService(db)
    approvals = await service.get_approval_history(current_user.id, limit)
    
    return [
        DocumentApprovalResponse(
            id=approval.id,
            file_id=approval.file_id,
            chat_session_id=approval.chat_session_id,
            title=approval.title,
            description=approval.description,
            change_type=approval.change_type,
            original_content=approval.original_content,
            proposed_content=approval.proposed_content,
            change_location=approval.change_location,
            change_metadata=approval.change_metadata,
            ai_reasoning=approval.ai_reasoning,
            confidence_score=approval.confidence_score,
            status=approval.status,
            approved_at=approval.approved_at,
            approved_by_user=approval.approved_by_user,
            expires_at=approval.expires_at,
            version_before=approval.version_before,
            version_after=approval.version_after,
            is_applied=approval.is_applied,
            applied_at=approval.applied_at,
            application_error=approval.application_error,
            created_at=approval.created_at,
            updated_at=approval.updated_at,
            file_name=approval.file.original_filename if approval.file else None
        )
        for approval in approvals
    ]


@router.post("/approvals/{approval_id}/decision", response_model=DocumentApprovalResponse)
async def process_approval_decision(
    approval_id: int,
    decision_request: ApprovalDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Process approval or rejection decision"""
    
    if decision_request.decision not in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
        raise HTTPException(
            status_code=400, 
            detail="Decision must be 'approved' or 'rejected'"
        )
    
    try:
        service = DocumentApprovalService(db)
        decision_request.approval_id = approval_id
        approval = await service.process_approval_decision(current_user.id, decision_request)
        
        return DocumentApprovalResponse(
            id=approval.id,
            file_id=approval.file_id,
            chat_session_id=approval.chat_session_id,
            title=approval.title,
            description=approval.description,
            change_type=approval.change_type,
            original_content=approval.original_content,
            proposed_content=approval.proposed_content,
            change_location=approval.change_location,
            change_metadata=approval.change_metadata,
            ai_reasoning=approval.ai_reasoning,
            confidence_score=approval.confidence_score,
            status=approval.status,
            approved_at=approval.approved_at,
            approved_by_user=approval.approved_by_user,
            expires_at=approval.expires_at,
            version_before=approval.version_before,
            version_after=approval.version_after,
            is_applied=approval.is_applied,
            applied_at=approval.applied_at,
            application_error=approval.application_error,
            created_at=approval.created_at,
            updated_at=approval.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process approval decision")


@router.get("/approvals/{approval_id}/diff", response_model=ContentDiffResponse)
async def get_approval_diff(
    approval_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content diff preview for an approval request"""
    
    try:
        service = DocumentApprovalService(db)
        diff = await service.generate_content_diff(approval_id, current_user.id)
        return diff
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate diff")


@router.post("/files/{file_id}/rollback/{version_number}")
async def rollback_file_version(
    file_id: int,
    version_number: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Rollback file to a specific version"""
    
    try:
        service = DocumentApprovalService(db)
        file, version = await service.rollback_to_version(
            file_id, current_user.id, version_number
        )
        return {
            "message": f"File rolled back to version {version_number}",
            "file_id": file.id,
            "version_number": version.version_number,
            "version_hash": version.version_hash
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to rollback file")


@router.get("/files/{file_id}/versions", response_model=VersionHistoryResponse)
async def get_file_version_history(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get version history for a file"""
    
    from app.models.document_approval import DocumentVersion
    from app.models.file import File
    from sqlalchemy import and_, select

    # Verify file ownership
    file_result = await db.execute(
        select(File).where(
            and_(File.id == file_id, File.user_id == current_user.id)
        )
    )
    file = file_result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get versions
    versions_result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.file_id == file_id)
        .order_by(DocumentVersion.version_number.desc())
    )
    versions = versions_result.scalars().all()
    
    current_version = max([v.version_number for v in versions]) if versions else 0
    
    return VersionHistoryResponse(
        file_id=file_id,
        file_name=file.original_filename,
        current_version=current_version,
        total_versions=len(versions),
        versions=[
            {
                "id": v.id,
                "file_id": v.file_id,
                "version_hash": v.version_hash,
                "version_number": v.version_number,
                "content_snapshot": v.content_snapshot[:1000] + "..." if len(v.content_snapshot) > 1000 else v.content_snapshot,
                "content_diff": v.content_diff,
                "change_summary": v.change_summary,
                "file_size": v.file_size,
                "file_metadata": v.file_metadata,
                "created_at": v.created_at
            }
            for v in versions
        ]
    )


@router.post("/maintenance/expire-approvals")
async def expire_old_approvals(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Expire old pending approval requests (admin/maintenance endpoint)"""
    
    service = DocumentApprovalService(db)
    expired_count = await service.expire_old_approvals()
    
    return {
        "message": f"Expired {expired_count} old approval requests",
        "expired_count": expired_count
    }
