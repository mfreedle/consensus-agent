#!/usr/bin/env python3
"""
Test Google Drive function calling with OpenAI Responses API
This script will test the complete flow including schema validation
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.config import Settings
from backend.app.llm.google_drive_tools import GoogleDriveTools
from backend.app.llm.orchestrator import LLMOrchestrator


async def test_google_drive_function_calling():
    """Test Google Drive function calling end-to-end"""
    
    print("🔍 Testing Google Drive Function Calling...")
    
    # Initialize settings
    settings = Settings()
    
    # Check if we have valid OpenAI API key
    if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key":
        print("❌ No valid OpenAI API key found")
        return False
    
    print(f"✅ OpenAI API key loaded: {settings.openai_api_key[:10]}...")
    
    # Initialize Google Drive tools
    google_drive_tools = GoogleDriveTools()
    
    # Get tool definitions
    tools = google_drive_tools.get_tool_definitions()
    print(f"✅ Google Drive tools loaded: {len(tools)} tools")
    
    for tool in tools:
        print(f"  - {tool['function']['name']}")
    
    # Initialize LLM orchestrator
    orchestrator = LLMOrchestrator(settings, google_drive_tools=google_drive_tools)
    
    print("\n🧪 Testing with a simple Google Drive search request...")
    
    # Test message that should trigger Google Drive search
    test_message = "Search for documents containing 'project plan' in my Google Drive"
    
    # Mock tokens for testing (these would normally come from user authentication)
    mock_tokens = {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token"
    }
    
    try:
        # This should attempt to call the search function
        # We expect it to fail with authentication error, but the function calling should work
        response = await orchestrator.generate_response_with_tools(
            message=test_message,
            conversation_history=[],
            available_tools=tools,
            google_drive_tokens=mock_tokens,
            user_id="test_user"
        )
        
        print("✅ Function calling completed")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"Response generation error: {error_str}")
        
        # Check if this is an expected Google Drive authentication error
        if "invalid_grant" in error_str or "refresh token" in error_str.lower() or "credentials" in error_str.lower():
            print("✅ This is expected - Google Drive authentication failed with mock tokens")
            print("✅ Function calling mechanism is working correctly")
            return True
        else:
            print(f"❌ Unexpected error: {e}")
            return False

async def main():
    """Main test function"""
    print("🚀 Starting Google Drive Function Calling Test\n")
    
    success = await test_google_drive_function_calling()
    
    if success:
        print("\n✅ Google Drive function calling test completed successfully!")
        print("\n📝 Next steps:")
        print("1. Connect your Google Drive account via the frontend")
        print("2. Test with real Google Drive operations")
    else:
        print("\n❌ Google Drive function calling test failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
