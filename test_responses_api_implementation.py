#!/usr/bin/env python3
"""
Test script to verify the new Responses API implementation for OpenAI function calling
"""

import asyncio
import logging
import os
import sys

# Add the backend to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.config import settings
from app.google.service import GoogleDriveService
from app.llm.google_drive_tools import GoogleDriveTools
from app.llm.orchestrator import llm_orchestrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_responses_api():
    """Test the new Responses API implementation"""
    
    print("🧪 Testing OpenAI Responses API Implementation")
    print("=" * 60)
    
    try:
        # Initialize Google Drive tools
        google_drive_service = GoogleDriveService(settings)
        google_drive_tools = GoogleDriveTools(google_drive_service)
        llm_orchestrator.set_google_drive_tools(google_drive_tools)
        
        # Create a test user (this would normally come from the database)
        class MockUser:
            def __init__(self):
                self.id = 1
                self.email = "test@example.com"
                self.google_drive_credentials = None
        
        user = MockUser()
        
        # Test 1: Simple function calling request
        print("\n📝 Test 1: Search for files in Google Drive")
        print("-" * 40)
        
        test_prompt = "Search for files named 'test' in my Google Drive and list what you find"
        
        try:
            response = await llm_orchestrator.get_openai_response_with_tools(
                prompt=test_prompt,
                user=user,
                model="gpt-4.1-mini",
                enable_google_drive=True
            )
            
            print(f"✅ Model: {response.model}")
            print(f"✅ Confidence: {response.confidence}")
            print(f"✅ Content preview: {response.content[:200]}...")
            
        except Exception as e:
            print(f"❌ Test 1 failed: {e}")
        
        # Test 2: File copy operation
        print("\n📝 Test 2: Copy file operation")
        print("-" * 40)
        
        test_prompt = "Find the file named 'Workshop Setup Guide' and copy it to the 'AI Workshop' folder"
        
        try:
            response = await llm_orchestrator.get_openai_response_with_tools(
                prompt=test_prompt,
                user=user,
                model="gpt-4.1-mini",
                enable_google_drive=True
            )
            
            print(f"✅ Model: {response.model}")
            print(f"✅ Confidence: {response.confidence}")
            print(f"✅ Content preview: {response.content[:200]}...")
            
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
        
        # Test 3: Check available tools
        print("\n📝 Test 3: Available Google Drive Tools")
        print("-" * 40)
        
        if google_drive_tools:
            functions = google_drive_tools.get_available_functions()
            print(f"✅ Available functions: {len(functions)}")
            for func in functions[:5]:  # Show first 5
                print(f"   • {func.name}: {func.description[:60]}...")
            if len(functions) > 5:
                print(f"   ... and {len(functions) - 5} more")
        else:
            print("❌ No Google Drive tools available")
        
        # Test 4: Fallback to Chat Completions API
        print("\n📝 Test 4: Fallback to Chat Completions API (GPT-4o)")
        print("-" * 40)
        
        try:
            response = await llm_orchestrator.get_openai_response_with_tools(
                prompt="What files are in my Google Drive?",
                user=user,
                model="gpt-4o",  # This should use Chat Completions API
                enable_google_drive=True
            )
            
            print(f"✅ Model: {response.model}")
            print(f"✅ Confidence: {response.confidence}")
            print(f"✅ Content preview: {response.content[:200]}...")
            
        except Exception as e:
            print(f"❌ Test 4 failed: {e}")
        
        print("\n🎉 Responses API testing completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_responses_api())
