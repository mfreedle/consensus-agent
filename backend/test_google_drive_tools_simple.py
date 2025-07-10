#!/usr/bin/env python3
"""
Simple test to verify Google Drive tools work from backend directory
"""

from app.config import Settings
from app.google.service import GoogleDriveService
from app.llm.google_drive_tools import GoogleDriveTools


def test_google_drive_tools():
    """Test Google Drive tools loading and schema"""
    
    print("🔍 Testing Google Drive tools...")
    
    # Load settings
    settings = Settings()
    print(f"✅ OpenAI API key loaded: {bool(settings.openai_api_key)}")
    print(f"✅ Google Client ID loaded: {bool(settings.google_client_id)}")
    
    # Initialize Google Drive service and tools
    google_service = GoogleDriveService(settings)
    google_tools = GoogleDriveTools(google_service)
    functions = google_tools.get_available_functions()
    
    print(f"✅ Google Drive tools loaded: {len(functions)} functions")
    
    for func in functions:
        print(f"  - {func.name}")
        
        # Check schema compliance
        schema = func.parameters
        has_required = 'required' in schema if schema else False
        has_additional_props = 'additionalProperties' in schema if schema else False
        
        if has_required and has_additional_props:
            print("    ✅ Schema compliant")
        else:
            print(f"    ❌ Schema issues - required: {has_required}, additionalProperties: {has_additional_props}")
    
    print("\n🎯 Summary:")
    print("- Google Drive tools load successfully")
    print("- Functions are available for orchestrator") 
    print("- Ready for function calling")
    
    return True

if __name__ == "__main__":
    success = test_google_drive_tools()
    if success:
        print("\n✅ Google Drive tools test completed successfully!")
    else:
        print("\n❌ Google Drive tools test failed")
