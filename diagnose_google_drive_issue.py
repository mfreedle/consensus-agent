#!/usr/bin/env python3
"""
Diagnostic script to debug the Google Drive function calling issue.
"""

import asyncio
import logging
import os
import sys

# Add backend to Python path
sys.path.append('./backend')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def diagnose_issue():
    """Diagnose the Google Drive function calling issue"""
    
    print("🔍 Diagnosing Google Drive Function Calling Issue")
    print("=" * 60)
    
    try:
        # Test 1: Check imports
        print("\n1. Testing imports...")
        from app.config import settings
        from app.google.service import GoogleDriveService
        from app.llm.google_drive_tools import GoogleDriveTools
        from app.llm.orchestrator import LLMOrchestrator
        print("✅ All imports successful")
        
        # Test 2: Check configuration
        print("\n2. Checking configuration...")
        print(f"OpenAI API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
        print(f"Google Client ID configured: {'Yes' if settings.google_client_id else 'No'}")
        print(f"Environment: {settings.app_env}")
        
        if not settings.openai_api_key:
            print("❌ OpenAI API key not configured! This will cause function calling to fail.")
            return False
        
        # Test 3: Test orchestrator initialization
        print("\n3. Testing orchestrator initialization...")
        orchestrator = LLMOrchestrator()
        print("✅ Orchestrator initialized")
        
        # Test 4: Test Google Drive tools setup
        print("\n4. Testing Google Drive tools setup...")
        google_service = GoogleDriveService(settings)
        google_drive_tools = GoogleDriveTools(google_service)
        orchestrator.set_google_drive_tools(google_drive_tools)
        print("✅ Google Drive tools configured")
        
        # Test 5: Test tool schema generation
        print("\n5. Testing tool schema generation...")
        tools = orchestrator._get_google_drive_tools_for_responses_api()
        print(f"✅ Generated {len(tools)} tool schemas")
        
        # Test 6: Test model support
        print("\n6. Testing model support...")
        models_to_test = ["gpt-4.1", "gpt-4.1-mini", "o3", "o3-mini"]
        for model in models_to_test:
            supports = orchestrator._supports_responses_api(model)
            print(f"  {model}: {'✅ Supported' if supports else '❌ Not supported'}")
        
        # Test 7: Test a simple OpenAI API call (without tools)
        print("\n7. Testing basic OpenAI API connectivity...")
        try:
            response = await orchestrator.get_openai_response(
                prompt="Hello, can you respond with just 'API test successful'?",
                model="gpt-4.1-mini",
                context=""
            )
            print(f"✅ Basic API call successful: {response.content[:50]}...")
        except Exception as api_error:
            print(f"❌ Basic API call failed: {api_error}")
            return False
        
        # Test 8: Test function calling format
        print("\n8. Testing function calling format...")
        sample_tool = tools[0] if tools else None
        if sample_tool:
            print(f"Sample tool name: {sample_tool['name']}")
            print(f"Has 'strict' flag: {'strict' in sample_tool and sample_tool['strict']}")
            print(f"Parameters structure valid: {'parameters' in sample_tool}")
            
            # Check if the schema is properly formatted
            params = sample_tool.get('parameters', {})
            has_required = 'required' in params
            has_additional_props = params.get('additionalProperties') is False
            has_properties = 'properties' in params
            
            print(f"Has required array: {has_required}")
            print(f"Has additionalProperties: false: {has_additional_props}")
            print(f"Has properties: {has_properties}")
            
            if has_required and has_additional_props and has_properties:
                print("✅ Schema format looks correct")
            else:
                print("❌ Schema format has issues")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 All diagnostic tests passed!")
        print("✅ Google Drive function calling should be working")
        print("\nPossible issues to check:")
        print("1. Check backend server logs for runtime errors")
        print("2. Verify user authentication is working")
        print("3. Check if Google Drive tokens are valid for the user")
        print("4. Verify socket.io connection is stable")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(diagnose_issue())
    if not success:
        print("\n❌ Please fix the issues above before testing function calling.")
        sys.exit(1)
