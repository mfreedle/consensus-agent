#!/usr/bin/env python3
"""
Test script to verify the tool format differences between APIs
"""

import json
import os
import sys

# Add the backend to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.config import settings
from app.google.service import GoogleDriveService
from app.llm.google_drive_tools import GoogleDriveTools
from app.llm.orchestrator import llm_orchestrator


def test_tool_formats():
    """Test that the tool formats are correct for different APIs"""
    
    print("🔧 Testing Tool Format Differences")
    print("=" * 50)
    
    try:
        # Initialize Google Drive tools
        google_drive_service = GoogleDriveService(settings)
        google_drive_tools = GoogleDriveTools(google_drive_service)
        llm_orchestrator.set_google_drive_tools(google_drive_tools)
        
        # Test 1: Chat Completions API format
        print("\n📝 Test 1: Chat Completions API Tool Format")
        print("-" * 40)
        
        chat_tools = llm_orchestrator._get_google_drive_tools_for_openai()
        
        if chat_tools:
            first_tool = chat_tools[0]
            print(f"✅ Number of tools: {len(chat_tools)}")
            print(f"✅ Tool structure: {list(first_tool.keys())}")
            print(f"✅ Has nested 'function': {'function' in first_tool}")
            
            if 'function' in first_tool:
                function_keys = list(first_tool['function'].keys())
                print(f"✅ Function keys: {function_keys}")
                print(f"✅ Function name: {first_tool['function'].get('name', 'NOT FOUND')}")
            
            print(f"✅ Sample tool format:")
            print(json.dumps(first_tool, indent=2)[:300] + "...")
        else:
            print("❌ No chat tools found")
        
        # Test 2: Responses API format
        print("\n📝 Test 2: Responses API Tool Format")
        print("-" * 40)
        
        responses_tools = llm_orchestrator._get_google_drive_tools_for_responses_api()
        
        if responses_tools:
            first_tool = responses_tools[0]
            print(f"✅ Number of tools: {len(responses_tools)}")
            print(f"✅ Tool structure: {list(first_tool.keys())}")
            print(f"✅ Has direct 'name': {'name' in first_tool}")
            print(f"✅ Has 'strict': {'strict' in first_tool}")
            print(f"✅ Tool name: {first_tool.get('name', 'NOT FOUND')}")
            
            print(f"✅ Sample tool format:")
            print(json.dumps(first_tool, indent=2)[:300] + "...")
        else:
            print("❌ No responses tools found")
        
        # Test 3: Compare formats
        print("\n📝 Test 3: Format Comparison")
        print("-" * 40)
        
        if chat_tools and responses_tools:
            chat_structure = set(chat_tools[0].keys())
            responses_structure = set(responses_tools[0].keys())
            
            print(f"✅ Chat Completions keys: {chat_structure}")
            print(f"✅ Responses API keys: {responses_structure}")
            
            if chat_structure != responses_structure:
                print("✅ Tool formats are different (correct)")
            else:
                print("❌ Tool formats are the same (incorrect)")
            
            # Verify specific requirements
            chat_has_function = 'function' in chat_tools[0]
            responses_has_name = 'name' in responses_tools[0]
            responses_has_strict = 'strict' in responses_tools[0]
            
            print(f"✅ Chat has nested function: {chat_has_function}")
            print(f"✅ Responses has direct name: {responses_has_name}")
            print(f"✅ Responses has strict: {responses_has_strict}")
            
            if chat_has_function and responses_has_name and responses_has_strict:
                print("🎉 All format requirements met!")
            else:
                print("❌ Some format requirements missing")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_formats()
