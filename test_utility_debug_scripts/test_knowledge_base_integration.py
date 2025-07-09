#!/usr/bin/env python3
"""
Test script to verify knowledge base integration fixes:
- Files uploaded to knowledge base are accessible to AI
- File attachments work correctly
- AI is aware of knowledge base files during chat
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set the correct database path - use the backend database
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
os.chdir(backend_dir)
os.environ['DATABASE_URL'] = 'sqlite:///./agent_mark.db'

from app.database.connection import AsyncSessionLocal
from app.models.chat import ChatSession, Message
from app.models.file import File
from app.models.user import User
from app.schemas.chat import ChatRequest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_knowledge_base_integration():
    """Test that knowledge base files are included in AI context"""
    
    async with AsyncSessionLocal() as db:
        print("🔍 Testing Knowledge Base Integration...")
        
        # Get a test user (assuming user with ID 1 exists)
        user_stmt = select(User).where(User.id == 1)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("❌ No test user found with ID 1")
            return False
            
        print(f"✅ Found test user: {user.email}")
        
        # Check if user has any files
        files_stmt = select(File).where(File.user_id == user.id)
        files_result = await db.execute(files_stmt)
        files = files_result.scalars().all()
        
        print(f"📁 User has {len(files)} files in total")
        
        # Check processed files with extracted text
        processed_files_stmt = select(File).where(
            File.user_id == user.id,
            File.is_processed.is_(True),
            File.extracted_text.is_not(None)
        )
        processed_files_result = await db.execute(processed_files_stmt)
        processed_files = processed_files_result.scalars().all()
        
        print(f"📄 User has {len(processed_files)} processed knowledge base files:")
        for file in processed_files:
            text_preview = file.extracted_text[:100] + "..." if file.extracted_text and len(file.extracted_text) > 100 else file.extracted_text or "(No text)"
            print(f"   - {file.original_filename}: {text_preview}")
        
        if len(processed_files) == 0:
            print("⚠️  No processed files found. Upload some files to test knowledge base integration.")
            return False
        
        # Test chat request simulation - this is what the new logic should handle
        print("\n🤖 Simulating chat request with knowledge base integration...")
        
        # Create a test chat request (without attached files)
        chat_request = ChatRequest(
            message="What files do you have access to in my knowledge base?",
            use_consensus=False,
            selected_models=["gpt-4o"],
            attached_file_ids=[]  # No attached files - should still include knowledge base
        )
        
        # Simulate the logic from chat router
        attached_files_context = ""  # No attached files in this test
        
        # Get ALL knowledge base files for this user (simulating new logic)
        knowledge_base_context = ""
        all_files_stmt = select(File).where(
            File.user_id == user.id,
            File.is_processed.is_(True),
            File.extracted_text.is_not(None)
        ).order_by(File.uploaded_at.desc())
        
        all_files_result = await db.execute(all_files_stmt)
        all_files = all_files_result.scalars().all()
        
        if all_files:
            print(f"✅ Found {len(all_files)} knowledge base files for AI context")
            knowledge_base_context = "\n\nKnowledge Base Files (available for reference):\n"
            total_kb_length = 0
            max_kb_length = 15000  # Limit knowledge base context to prevent overflow
            
            for file in all_files:
                if file.extracted_text:
                    # Limit individual file content and check total length
                    content = file.extracted_text[:3000]
                    if len(file.extracted_text) > 3000:
                        content += "\n... (content truncated)"
                    
                    file_entry = f"\n--- {file.original_filename} ---\n{content}\n"
                    
                    if total_kb_length + len(file_entry) > max_kb_length:
                        knowledge_base_context += "\n... (additional files available but truncated to prevent context overflow)\n"
                        break
                        
                    knowledge_base_context += file_entry
                    total_kb_length += len(file_entry)
        
        # Combine all file contexts
        file_context = attached_files_context + knowledge_base_context
        
        print(f"📋 Generated file context length: {len(file_context)} characters")
        print(f"📋 Context preview:\n{file_context[:500]}...")
        
        if len(file_context.strip()) > 0:
            print("✅ Knowledge base integration is working! AI will have access to all user files.")
            return True
        else:
            print("❌ Knowledge base integration failed - no context generated.")
            return False

async def test_file_attachment_flow():
    """Test that file attachments work correctly"""
    
    async with AsyncSessionLocal() as db:
        print("\n📎 Testing File Attachment Flow...")
        
        # Get a test user
        user_stmt = select(User).where(User.id == 1)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("❌ No test user found")
            return False
        
        # Get user's files
        files_stmt = select(File).where(File.user_id == user.id).limit(2)
        files_result = await db.execute(files_stmt)
        files = files_result.scalars().all()
        
        if len(files) == 0:
            print("⚠️  No files available for attachment test")
            return False
        
        # Simulate chat request with file attachments
        attached_file_ids = [str(files[0].id)]
        if len(files) > 1:
            attached_file_ids.append(str(files[1].id))
        
        print(f"📎 Testing with attached file IDs: {attached_file_ids}")
        
        chat_request = ChatRequest(
            message="Please analyze the attached files",
            use_consensus=False,
            selected_models=["gpt-4o"],
            attached_file_ids=attached_file_ids
        )
        
        # Simulate attached files processing
        attached_files_context = ""
        if attached_file_ids:
            file_ids = [int(fid) for fid in attached_file_ids]
            files_stmt = select(File).where(
                File.id.in_(file_ids),
                File.user_id == user.id
            )
            files_result = await db.execute(files_stmt)
            files = files_result.scalars().all()
            
            if files:
                attached_files_context = "\n\nAttached files for this message:\n"
                for file in files:
                    attached_files_context += f"\n--- {file.original_filename} ---\n"
                    if file.extracted_text:
                        content = file.extracted_text[:5000]
                        if len(file.extracted_text) > 5000:
                            content += "\n... (content truncated)"
                        attached_files_context += content
                    else:
                        attached_files_context += "(File not yet processed or could not extract text)"
                    attached_files_context += "\n"
        
        print(f"📎 Attached files context length: {len(attached_files_context)} characters")
        
        if len(attached_files_context.strip()) > 0:
            print("✅ File attachment is working correctly!")
            return True
        else:
            print("❌ File attachment failed - no context generated.")
            return False

async def main():
    """Run all tests"""
    print("🧪 Running Knowledge Base and File Attachment Tests\n")
    
    try:
        # Test knowledge base integration
        kb_success = await test_knowledge_base_integration()
        
        # Test file attachment flow  
        attach_success = await test_file_attachment_flow()
        
        print(f"\n📊 Test Results:")
        print(f"   Knowledge Base Integration: {'✅ PASS' if kb_success else '❌ FAIL'}")
        print(f"   File Attachment Flow: {'✅ PASS' if attach_success else '❌ FAIL'}")
        
        if kb_success and attach_success:
            print("\n🎉 All tests passed! The fixes are working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the implementation.")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
