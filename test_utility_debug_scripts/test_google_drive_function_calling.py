#!/usr/bin/env python3
"""
Test script to specifically test the Google Drive function calling with Responses API.
This simulates the exact call that would be made from the socket handler.
"""

import asyncio
import json
import os
import sys

# Add backend to Python path
sys.path.append('./backend')

# Load environment variables like the main app does
from dotenv import load_dotenv

# Load from backend/.env since that's where the .env file is located
load_dotenv('./backend/.env')

async def test_google_drive_function_calling():
    """Test the exact function calling scenario that's failing"""
    
    print("🧪 Testing Google Drive Function Calling with Responses API")
    print("=" * 65)
    
    try:
        # Import and setup exactly like the backend does
        from app.config import settings
        from app.google.service import GoogleDriveService
        from app.llm.google_drive_tools import GoogleDriveTools
        from app.llm.orchestrator import LLMOrchestrator
        
        print("✅ Imports successful")
        
        # Check configuration
        if not settings.openai_api_key:
            print("❌ OpenAI API key not configured!")
            print("The backend needs an OpenAI API key to function.")
            print("Please set OPENAI_API_KEY in the environment or .env file.")
            return False
        
        print(f"✅ OpenAI API key configured: {settings.openai_api_key[:20]}...")
        
        # Setup orchestrator exactly like backend does
        llm_orchestrator = LLMOrchestrator()
        google_service = GoogleDriveService(settings)
        google_drive_tools = GoogleDriveTools(google_service)
        llm_orchestrator.set_google_drive_tools(google_drive_tools)
        
        print("✅ Orchestrator and tools configured")
        
        # Create a mock user object (normally comes from authentication)
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "test_user"
                self.google_drive_token = None  # This would normally have a real token
                self.google_refresh_token = None
        
        user = MockUser()
        
        # Test the exact message that was sent
        test_message = "Hello, In my AI Workshop folder there is a file named one_pager_v03.md. Please make a copy of it and put the copy in the main Google Drive folder."
        
        print(f"\n📝 Testing message: {test_message[:60]}...")
        
        # Test the exact call that the socket handler makes
        print("\n🚀 Making Responses API call with Google Drive tools...")
        
        # This is the exact call from sio_events.py line 401
        response = await llm_orchestrator.get_openai_response_with_tools(
            prompt=test_message,
            user=user,
            model="gpt-4.1",  # The model from the console log
            context="",
            enable_google_drive=True
        )
        
        print(f"\n✅ Response received!")
        print(f"Response length: {len(response.content)}")
        print(f"Response preview: {response.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_google_drive_function_calling())
    if success:
        print("\n🎉 Test completed successfully!")
        print("The issue may be in the socket handling, authentication, or deployment.")
    else:
        print("\n❌ Test failed. This explains why the LLM isn't responding.")
        print("Fix the issues above to resolve the problem.")
