#!/usr/bin/env python3
"""Debug script to test approval history endpoint directly"""

import asyncio
from app.database.connection import get_db
from app.files.approval_service import DocumentApprovalService
from app.schemas.document_approval import DocumentApprovalResponse

async def test_history_endpoint():
    """Test the approval history service directly"""
    
    # Get database session
    async for db in get_db():
        try:
            print("🔍 Testing approval history service...")
            
            # Create service
            service = DocumentApprovalService(db)
            
            # Test with user_id 1 (from our tests)
            user_id = 1
            print(f"Getting approval history for user {user_id}...")
            
            # Get approvals
            approvals = await service.get_approval_history(user_id, 50)
            print(f"✅ Found {len(approvals)} approvals")
            
            # Try to convert each approval to response model
            for i, approval in enumerate(approvals):
                print(f"\n--- Approval {i+1} (ID: {approval.id}) ---")
                print(f"Status: {approval.status}")
                print(f"Change type: {approval.change_type}")
                print(f"Title: {approval.title}")
                
                try:
                    # Try to create the response model
                    response = DocumentApprovalResponse(
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
                        file_name=None,
                        chat_session_title=None
                    )
                    print("✅ Response model created successfully")
                    
                except Exception as e:
                    print(f"❌ Error creating response model: {e}")
                    print(f"   Approval status type: {type(approval.status)}")
                    print(f"   Approval status value: {approval.status}")
                    print(f"   Change type: {type(approval.change_type)}")
                    print(f"   Change type value: {approval.change_type}")
                    raise
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        break

if __name__ == "__main__":
    asyncio.run(test_history_endpoint())
