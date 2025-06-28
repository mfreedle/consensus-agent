import difflib
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app.models.document_approval import (ApprovalStatus, ApprovalTemplate,
                                          ChangeType, DocumentApproval,
                                          DocumentVersion)
from app.models.file import File
from app.models.user import User
from app.schemas.document_approval import (ApprovalDecisionRequest,
                                           ApprovalPreviewResponse,
                                           ContentDiffResponse,
                                           CreateApprovalRequest,
                                           DocumentApprovalResponse)
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class DocumentApprovalService:
    """Service for managing document approval workflow"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_approval_request(
        self, 
        user_id: int, 
        request: CreateApprovalRequest
    ) -> DocumentApproval:
        """Create a new document approval request"""
        
        # Verify file exists and belongs to user
        file_result = await self.db.execute(
            select(File).where(
                and_(File.id == request.file_id, File.user_id == user_id)
            )
        )
        file = file_result.scalar_one_or_none()
        if not file:
            raise ValueError("File not found or access denied")
        
        # Generate version hash for current content
        current_content = file.extracted_text or ""
        version_before = self._generate_content_hash(current_content)
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(hours=request.expires_in_hours or 24)
        
        # Create approval request
        # Convert Pydantic enum to SQLAlchemy enum if needed
        change_type_value = request.change_type
        if isinstance(change_type_value, str):
            # Convert string to enum
            change_type_value = ChangeType(change_type_value)
        
        approval = DocumentApproval(
            user_id=user_id,
            file_id=request.file_id,
            chat_session_id=request.chat_session_id,
            title=request.title,
            description=request.description,
            change_type=change_type_value,
            original_content=request.original_content,
            proposed_content=request.proposed_content,
            change_location=request.change_location,
            change_metadata=request.change_metadata,
            ai_reasoning=request.ai_reasoning,
            confidence_score=request.confidence_score,
            expires_at=expires_at,
            version_before=version_before,
            status=ApprovalStatus.PENDING
        )
        
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        
        # Check if this matches any auto-approval templates
        await self._check_auto_approval(approval)
        
        return approval
    
    async def process_approval_decision(
        self, 
        user_id: int, 
        request: ApprovalDecisionRequest
    ) -> DocumentApproval:
        """Process approval or rejection decision"""
        
        # Get approval request
        result = await self.db.execute(
            select(DocumentApproval).where(
                and_(
                    DocumentApproval.id == request.approval_id,
                    DocumentApproval.user_id == user_id,
                    DocumentApproval.status == ApprovalStatus.PENDING
                )
            )
        )
        approval = result.scalar_one_or_none()
        if not approval:
            raise ValueError("Approval request not found or already processed")
        
        # Update approval status
        approval.status = request.decision
        approval.approved_at = datetime.utcnow()
        approval.approved_by_user = True
        
        # If approved, apply the changes
        if request.decision == ApprovalStatus.APPROVED:
            await self._apply_document_changes(approval)
        
        await self.db.commit()
        return approval
    
    async def get_pending_approvals(
        self, 
        user_id: int, 
        limit: int = 20
    ) -> List[DocumentApproval]:
        """Get pending approval requests for user"""
        
        result = await self.db.execute(
            select(DocumentApproval)
            .options(selectinload(DocumentApproval.file))
            .where(
                and_(
                    DocumentApproval.user_id == user_id,
                    DocumentApproval.status == ApprovalStatus.PENDING,
                    or_(
                        DocumentApproval.expires_at.is_(None),
                        DocumentApproval.expires_at > datetime.utcnow()
                    )
                )
            )
            .order_by(desc(DocumentApproval.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_approval_history(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[DocumentApproval]:
        """Get approval history for user"""
        
        result = await self.db.execute(
            select(DocumentApproval)
            .options(selectinload(DocumentApproval.file))
            .where(DocumentApproval.user_id == user_id)
            .order_by(desc(DocumentApproval.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def generate_content_diff(
        self, 
        approval_id: int, 
        user_id: int
    ) -> ContentDiffResponse:
        """Generate diff preview for approval request"""
        
        result = await self.db.execute(
            select(DocumentApproval)
            .options(selectinload(DocumentApproval.file))
            .where(
                and_(
                    DocumentApproval.id == approval_id,
                    DocumentApproval.user_id == user_id
                )
            )
        )
        approval = result.scalar_one_or_none()
        if not approval:
            raise ValueError("Approval request not found")
        
        # Get original and proposed content
        original_content = approval.original_content or approval.file.extracted_text or ""
        proposed_content = approval.proposed_content
        
        # Generate diff
        original_lines = original_content.splitlines(keepends=True)
        proposed_lines = proposed_content.splitlines(keepends=True)
        
        # Create unified diff
        diff_lines = list(difflib.unified_diff(
            original_lines,
            proposed_lines,
            fromfile=f"{approval.file.original_filename} (original)",
            tofile=f"{approval.file.original_filename} (proposed)",
            lineterm=""
        ))
        
        # Generate HTML diff
        html_diff = difflib.HtmlDiff()
        diff_html = html_diff.make_table(
            original_lines,
            proposed_lines,
            fromdesc="Original",
            todesc="Proposed",
            context=True,
            numlines=3
        )
        
        # Calculate statistics
        differ = difflib.SequenceMatcher(None, original_lines, proposed_lines)
        opcodes = differ.get_opcodes()
        
        lines_added = sum(1 for tag, _, _, _, _ in opcodes if tag == 'insert')
        lines_removed = sum(1 for tag, _, _, _, _ in opcodes if tag == 'delete')
        lines_modified = sum(1 for tag, _, _, _, _ in opcodes if tag == 'replace')
        
        # Generate summary
        change_summary = self._generate_change_summary(approval, lines_added, lines_removed, lines_modified)
        
        return ContentDiffResponse(
            original_lines=original_lines,
            proposed_lines=proposed_lines,
            diff_html=diff_html,
            diff_text="\n".join(diff_lines),
            change_summary=change_summary,
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified
        )
    
    async def create_document_version(
        self, 
        file_id: int, 
        user_id: int, 
        content: str,
        approval_id: Optional[int] = None,
        change_summary: Optional[str] = None
    ) -> DocumentVersion:
        """Create a new document version"""
        
        # Get current version number
        result = await self.db.execute(
            select(func.max(DocumentVersion.version_number))
            .where(DocumentVersion.file_id == file_id)
        )
        max_version = result.scalar() or 0
        new_version = max_version + 1
        
        # Generate content hash
        content_hash = self._generate_content_hash(content)
        
        # Get previous version for diff
        content_diff = None
        if max_version > 0:
            prev_result = await self.db.execute(
                select(DocumentVersion.content_snapshot)
                .where(
                    and_(
                        DocumentVersion.file_id == file_id,
                        DocumentVersion.version_number == max_version
                    )
                )
            )
            prev_content = prev_result.scalar()
            if prev_content:
                content_diff = self._generate_text_diff(prev_content, content)
        
        # Create version record
        version = DocumentVersion(
            file_id=file_id,
            user_id=user_id,
            approval_id=approval_id,
            version_hash=content_hash,
            version_number=new_version,
            content_snapshot=content,
            content_diff=content_diff,
            change_summary=change_summary,
            file_size=len(content.encode('utf-8'))
        )
        
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        
        return version
    
    async def rollback_to_version(
        self, 
        file_id: int, 
        user_id: int, 
        version_number: int
    ) -> Tuple[File, DocumentVersion]:
        """Rollback file to a specific version"""
        
        # Verify file ownership
        file_result = await self.db.execute(
            select(File).where(
                and_(File.id == file_id, File.user_id == user_id)
            )
        )
        file = file_result.scalar_one_or_none()
        if not file:
            raise ValueError("File not found or access denied")
        
        # Get target version
        version_result = await self.db.execute(
            select(DocumentVersion).where(
                and_(
                    DocumentVersion.file_id == file_id,
                    DocumentVersion.version_number == version_number
                )
            )
        )
        target_version = version_result.scalar_one_or_none()
        if not target_version:
            raise ValueError("Version not found")
        
        # Update file content
        file.extracted_text = target_version.content_snapshot
        file.updated_at = datetime.utcnow()
        
        # Create new version record for the rollback
        await self.create_document_version(
            file_id=file_id,
            user_id=user_id,
            content=target_version.content_snapshot,
            change_summary=f"Rollback to version {version_number}"
        )
        
        await self.db.commit()
        return file, target_version
    
    async def expire_old_approvals(self) -> int:
        """Expire old pending approval requests"""
        
        result = await self.db.execute(
            select(DocumentApproval).where(
                and_(
                    DocumentApproval.status == ApprovalStatus.PENDING,
                    DocumentApproval.expires_at < datetime.utcnow()
                )
            )
        )
        expired_approvals = result.scalars().all()
        
        for approval in expired_approvals:
            approval.status = ApprovalStatus.EXPIRED
        
        await self.db.commit()
        return len(expired_approvals)
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _generate_text_diff(self, old_content: str, new_content: str) -> str:
        """Generate text diff between two content versions"""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff_lines = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm=""
        ))
        
        return "\n".join(diff_lines)
    
    def _generate_change_summary(
        self, 
        approval: DocumentApproval, 
        added: int, 
        removed: int, 
        modified: int
    ) -> str:
        """Generate human-readable change summary"""
        
        parts = []
        
        if added > 0:
            parts.append(f"{added} line(s) added")
        if removed > 0:
            parts.append(f"{removed} line(s) removed")
        if modified > 0:
            parts.append(f"{modified} line(s) modified")
        
        if not parts:
            return "No changes detected"
        
        summary = ", ".join(parts)
        
        if approval.change_type == ChangeType.CONTENT_EDIT:
            return f"Content edit: {summary}"
        elif approval.change_type == ChangeType.CONTENT_APPEND:
            return f"Content appended: {summary}"
        elif approval.change_type == ChangeType.CONTENT_INSERT:
            return f"Content inserted: {summary}"
        elif approval.change_type == ChangeType.CONTENT_DELETE:
            return f"Content deleted: {summary}"
        else:
            return f"Document modified: {summary}"
    
    async def _check_auto_approval(self, approval: DocumentApproval) -> None:
        """Check if approval matches auto-approval templates"""
        
        result = await self.db.execute(
            select(ApprovalTemplate).where(
                and_(
                    ApprovalTemplate.user_id == approval.user_id,
                    ApprovalTemplate.is_active == True
                )
            )
        )
        templates = result.scalars().all()
        
        for template in templates:
            # Check if change type matches template
            if approval.change_type.value not in template.change_types:
                continue
                
            # Check confidence threshold
            if (approval.confidence_score is not None and 
                approval.confidence_score >= template.max_confidence_required):
                
                # Check file type filter
                file_result = await self.db.execute(
                    select(File.file_type).where(File.id == approval.file_id)
                )
                file_type = file_result.scalar()
                
                if (template.file_type_filter is None or 
                    file_type == template.file_type_filter):
                    
                    # Auto-approve
                    approval.status = ApprovalStatus.APPROVED
                    approval.approved_at = datetime.utcnow()
                    approval.approved_by_user = False
                    
                    # Apply changes
                    await self._apply_document_changes(approval)
                    break
    
    async def _apply_document_changes(self, approval: DocumentApproval) -> None:
        """Apply approved changes to the document"""
        
        try:
            # Get the file
            file_result = await self.db.execute(
                select(File).where(File.id == approval.file_id)
            )
            file = file_result.scalar_one()
            
            # Create version snapshot before changes
            if file.extracted_text:
                await self.create_document_version(
                    file_id=file.id,
                    user_id=approval.user_id,
                    content=file.extracted_text,
                    change_summary="Pre-approval snapshot"
                )
            
            # Apply the changes based on change type
            if approval.change_type == ChangeType.CONTENT_EDIT:
                file.extracted_text = approval.proposed_content
            elif approval.change_type == ChangeType.CONTENT_APPEND:
                current_content = file.extracted_text or ""
                file.extracted_text = current_content + approval.proposed_content
            elif approval.change_type == ChangeType.CONTENT_INSERT:
                # For inserts, use change_location to determine where to insert
                current_content = file.extracted_text or ""
                if approval.change_location and 'line_number' in approval.change_location:
                    lines = current_content.splitlines()
                    insert_line = approval.change_location['line_number']
                    lines.insert(insert_line, approval.proposed_content)
                    file.extracted_text = "\n".join(lines)
                else:
                    # Fallback to append
                    file.extracted_text = current_content + approval.proposed_content
            elif approval.change_type == ChangeType.CONTENT_DELETE:
                # Replace original content with empty or remove specified content
                if approval.original_content:
                    current_content = file.extracted_text or ""
                    file.extracted_text = current_content.replace(approval.original_content, "")
                # Note: More sophisticated deletion logic could be implemented
            
            # Update file metadata
            file.updated_at = datetime.utcnow()
            
            # Generate version hash after changes
            approval.version_after = self._generate_content_hash(file.extracted_text)
            
            # Create version snapshot after changes
            await self.create_document_version(
                file_id=file.id,
                user_id=approval.user_id,
                content=file.extracted_text,
                approval_id=approval.id,
                change_summary=approval.title
            )
            
            # Mark as applied
            approval.is_applied = True
            approval.applied_at = datetime.utcnow()
            
        except Exception as e:
            approval.application_error = str(e)
            raise
