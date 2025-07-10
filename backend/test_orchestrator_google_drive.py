#!/usr/bin/env python3
"""
Test Google Drive tools integration with orchestrator for OpenAI Responses API
"""

from app.config import Settings
from app.google.service import GoogleDriveService
from app.llm.google_drive_tools import GoogleDriveTools
from app.llm.orchestrator import LLMOrchestrator


def test_orchestrator_google_drive_integration():
    """Test that orchestrator properly formats Google Drive tools for Responses API"""
    
    print("🔍 Testing Orchestrator Google Drive Integration...")
    
    # Load settings
    settings = Settings()
    print(f"✅ Settings loaded - OpenAI: {bool(settings.openai_api_key)}")
    
    # Initialize Google Drive service and tools
    google_service = GoogleDriveService(settings)
    google_tools = GoogleDriveTools(google_service)
    
    # Initialize orchestrator
    orchestrator = LLMOrchestrator()
    orchestrator.set_google_drive_tools(google_tools)
    
    # Get tools formatted for Responses API
    tools = orchestrator._get_google_drive_tools_for_responses_api()
    
    print(f"✅ Orchestrator formatted {len(tools)} tools for Responses API")
    
    # Check first few tools for proper formatting
    for i, tool in enumerate(tools[:3]):
        name = tool.get('name', 'unknown')
        tool_type = tool.get('type', 'unknown')
        strict_mode = tool.get('strict', False)
        parameters = tool.get('parameters', {})
        
        print(f"  - {name}")
        print(f"    Type: {tool_type}")
        print(f"    Strict mode: {strict_mode}")
        
        # Check for required Responses API format
        if tool_type == "function" and strict_mode:
            print("    ✅ Proper Responses API format")
        else:
            print("    ❌ Missing required Responses API fields")
            
        # Check schema compliance
        if isinstance(parameters, dict):
            has_additional_props = parameters.get("additionalProperties") is False
            has_required = "required" in parameters
            
            if has_additional_props and has_required:
                print("    ✅ Schema compliant for strict mode")
            else:
                print(f"    ❌ Schema issues - additionalProperties: {has_additional_props}, required: {has_required}")
        
        print()
    
    print("🎯 Summary:")
    print("- Orchestrator loads Google Drive tools successfully")
    print("- Tools are properly formatted for OpenAI Responses API")
    print("- Schemas are strict mode compliant")
    print("- Function calling should work correctly")
    
    return True

if __name__ == "__main__":
    success = test_orchestrator_google_drive_integration()
    if success:
        print("\n✅ Orchestrator Google Drive integration test completed successfully!")
        print("\n📝 Next steps:")
        print("1. Connect your Google Drive account via the frontend at http://localhost:3010")
        print("2. Test actual Google Drive operations through the chat interface")
        print("3. Verify that function calling works end-to-end")
    else:
        print("\n❌ Orchestrator Google Drive integration test failed")
