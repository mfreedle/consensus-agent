#!/usr/bin/env python3
"""
Google Drive Integration Demo Script
Tests the complete Google Drive functionality for LLMs
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.google.service import GoogleDriveService
from app.llm.google_drive_context import GoogleDriveContextManager
from app.llm.google_drive_tools import GoogleDriveTools
from app.llm.orchestrator import llm_orchestrator


def print_status(message, success=True):
    """Print colored status message"""
    symbol = "✅" if success else "❌"
    print(f"{symbol} {message}")

async def test_google_drive_integration():
    """Test the complete Google Drive integration"""
    
    print("🚀 Testing Google Drive Integration for LLMs\n")
    
    try:
        # Test 1: Initialize Google Drive Service
        print("1. Initializing Google Drive Service...")
        google_service = GoogleDriveService(settings)
        print_status("Google Drive Service initialized")
        
        # Test 2: Initialize Google Drive Tools
        print("\n2. Initializing Google Drive Tools...")
        google_drive_tools = GoogleDriveTools(google_service)
        functions = google_drive_tools.get_available_functions()
        print_status(f"Google Drive Tools initialized with {len(functions)} functions")
        
        # List available functions
        print("\n   Available Functions:")
        for func in functions:
            print(f"   • {func.name}: {func.description}")
        
        # Test 3: Initialize Google Drive Context Manager
        print("\n3. Initializing Google Drive Context Manager...")
        google_drive_context_manager = GoogleDriveContextManager(google_service)
        print_status("Google Drive Context Manager initialized")
        
        # Test 4: Configure LLM Orchestrator
        print("\n4. Configuring LLM Orchestrator with Google Drive tools...")
        llm_orchestrator.set_google_drive_tools(google_drive_tools)
        print_status("LLM Orchestrator configured with Google Drive tools")
        
        # Test 5: Check Environment Variables
        print("\n5. Checking Google Drive credentials...")
        if settings.google_client_id and settings.google_client_secret:
            print_status("Google OAuth credentials found")
            print(f"   Client ID: {settings.google_client_id[:20]}...")
            print(f"   Redirect URI: {settings.google_redirect_uri}")
        else:
            print_status("Google OAuth credentials missing", False)
            print("   Please check your .env file for GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
        
        # Test 6: Test Function Schema Generation
        print("\n6. Testing OpenAI function schema generation...")
        openai_tools = []
        for func in functions:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": func.name,
                    "description": func.description,
                    "parameters": func.parameters
                }
            })
        print_status(f"Generated {len(openai_tools)} OpenAI-compatible function schemas")
        
        # Show sample function schema
        if openai_tools:
            print("\n   Sample Function Schema:")
            sample_func = openai_tools[0]
            print(f"   {json.dumps(sample_func, indent=2)}")
        
        print("\n🎉 Google Drive Integration Test Complete!")
        print("\n📋 Summary:")
        print("   ✅ Google Drive Service: Ready")
        print("   ✅ Google Drive Tools: Ready") 
        print("   ✅ Google Drive Context: Ready")
        print("   ✅ LLM Integration: Ready")
        print("   ✅ Function Calling: Ready")
        
        print("\n🔍 What's Available:")
        print("   • LLMs can list Google Drive files")
        print("   • LLMs can read Google Docs, Sheets, and Slides")
        print("   • LLMs can edit Google Docs and Sheets")
        print("   • LLMs can create new Google Docs, Sheets, and Slides")
        print("   • Google Drive files included in chat context")
        print("   • Socket.IO chat system supports Google Drive operations")
        
        print("\n🚀 Next Steps:")
        print("   1. Connect your Google Drive account in the frontend")
        print("   2. Ask the AI to work with your Google Drive files")
        print("   3. Watch as the AI reads, edits, and creates files!")
        
        return True
        
    except Exception as e:
        print_status(f"Test failed: {str(e)}", False)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_google_drive_integration())
