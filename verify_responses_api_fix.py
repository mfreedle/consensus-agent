#!/usr/bin/env python3
"""
Verification script to confirm the OpenAI Responses API fix is properly implemented
"""

import os
import sys

# Add the backend to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def verify_responses_api_fix():
    """Verify that the Responses API fix is properly implemented"""
    
    print("🔍 Verifying OpenAI Responses API Fix Implementation")
    print("=" * 60)
    
    # Check 1: Verify orchestrator has Responses API code
    print("\n📝 Check 1: Orchestrator Implementation")
    print("-" * 40)
    
    try:
        with open('backend/app/llm/orchestrator.py', 'r', encoding='utf-8') as f:
            orchestrator_content = f.read()
        
        # Check for Responses API usage
        if 'responses.create' in orchestrator_content:
            print("✅ Responses API implementation found")
        else:
            print("❌ Responses API implementation NOT found")
        
        # Check for model routing
        if 'gpt-4.1-mini' in orchestrator_content and 'o3' in orchestrator_content:
            print("✅ Model routing for new models found")
        else:
            print("❌ Model routing NOT properly configured")
        
        # Check for tool_choice required (with quotes)
        if '"required"' in orchestrator_content or "'required'" in orchestrator_content:
            print("✅ Forced tool usage (tool_choice='required') found")
        else:
            print("❌ Forced tool usage NOT found")
            
    except FileNotFoundError:
        print("❌ orchestrator.py file not found")
    
    # Check 2: Verify default model change
    print("\n📝 Check 2: Default Model Configuration")
    print("-" * 40)
    
    try:
        with open('backend/app/sio_events.py', 'r', encoding='utf-8') as f:
            sio_content = f.read()
        
        # Check for gpt-4.1-mini as default
        if 'gpt-4.1-mini' in sio_content:
            print("✅ Default model changed to gpt-4.1-mini")
        else:
            print("❌ Default model NOT changed")
            
    except FileNotFoundError:
        print("❌ sio_events.py file not found")
    
    # Check 3: Verify Google Drive tools are available
    print("\n📝 Check 3: Google Drive Tools Integration")
    print("-" * 40)
    
    try:
        from app.config import settings
        from app.google.service import GoogleDriveService
        from app.llm.google_drive_tools import GoogleDriveTools

        # Initialize tools
        google_drive_service = GoogleDriveService(settings)
        google_drive_tools = GoogleDriveTools(google_drive_service)
        
        # Check available functions
        functions = google_drive_tools.get_available_functions()
        print(f"✅ Google Drive tools available: {len(functions)} functions")
        
        # Check for key functions
        function_names = [f.name for f in functions]
        key_functions = ['search_google_drive_files', 'copy_google_drive_file', 'move_google_drive_file', 'list_folder_contents']
        
        for func_name in key_functions:
            if func_name in function_names:
                print(f"✅ {func_name} function available")
            else:
                print(f"❌ {func_name} function NOT available")
                
    except Exception as e:
        print(f"❌ Error checking Google Drive tools: {e}")
    
    # Check 4: Verify OpenAI Function Calling Guide is available
    print("\n📝 Check 4: OpenAI Function Calling Guide")
    print("-" * 40)
    
    try:
        with open('docs/external/OpenAI_Function_Calling_Guide.md', 'r', encoding='utf-8') as f:
            guide_content = f.read()
        
        if 'responses.create' in guide_content:
            print("✅ OpenAI Function Calling Guide with Responses API found")
        else:
            print("❌ OpenAI Function Calling Guide NOT found or incomplete")
            
    except FileNotFoundError:
        print("❌ OpenAI Function Calling Guide file not found")
    
    print("\n🎉 Verification completed!")
    print("=" * 60)
    print("\n📋 Summary:")
    print("The fix implements OpenAI's latest Responses API for GPT-4.1 and newer models,")
    print("ensuring that LLMs actually execute functions instead of just describing them.")
    print("\n🚀 Next: Test with actual user interactions to verify function execution!")

if __name__ == "__main__":
    verify_responses_api_fix()
