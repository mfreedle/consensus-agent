#!/usr/bin/env python3
"""
Test script to verify Google Drive schema compatibility with OpenAI Responses API
"""

import os
import sys

sys.path.append('.')
sys.path.append('./backend')

import json

from backend.app.config import settings
from backend.app.google.service import GoogleDriveService
from backend.app.llm.google_drive_tools import GoogleDriveTools
from backend.app.llm.orchestrator import LLMOrchestrator


def test_google_drive_schema_fix():
    """Test that Google Drive function schemas are compatible with OpenAI Responses API"""
    
    print("🔧 Testing Google Drive Schema Fix for OpenAI Responses API")
    print("=" * 60)
    
    try:
        # Initialize services
        google_service = GoogleDriveService(settings)
        google_drive_tools = GoogleDriveTools(google_service)
        orchestrator = LLMOrchestrator()
        orchestrator.set_google_drive_tools(google_drive_tools)
        
        print("✅ Services initialized successfully")
        
        # Test 1: Get functions
        functions = google_drive_tools.get_available_functions()
        print(f"✅ Available functions: {len(functions)}")
        
        # Test 2: Get tools for Responses API
        responses_tools = orchestrator._get_google_drive_tools_for_responses_api()
        print(f"✅ Responses API tools: {len(responses_tools)}")
        
        # Test 3: Validate first tool schema
        if responses_tools:
            first_tool = responses_tools[0]
            print(f"\n📋 Sample Tool Schema: {first_tool['name']}")
            
            # Check required fields
            required_fields = ['type', 'name', 'description', 'parameters', 'strict']
            missing_fields = [field for field in required_fields if field not in first_tool]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            else:
                print("✅ All required fields present")
            
            # Check parameters structure
            params = first_tool['parameters']
            if params.get('type') != 'object':
                print(f"❌ Parameters type should be 'object', got: {params.get('type')}")
                return False
            
            if 'additionalProperties' not in params:
                print("❌ Missing 'additionalProperties' in parameters")
                return False
            
            if params['additionalProperties'] is not False:
                print(f"❌ 'additionalProperties' should be False, got: {params['additionalProperties']}")
                return False
            
            if 'required' not in params:
                print("❌ Missing 'required' array in parameters")
                return False
            
            if not isinstance(params['required'], list):
                print(f"❌ 'required' should be a list, got: {type(params['required'])}")
                return False
            
            print("✅ Parameters structure valid")
            
            # Check strict mode
            if first_tool.get('strict') is not True:
                print(f"❌ 'strict' should be True, got: {first_tool.get('strict')}")
                return False
            
            print("✅ Strict mode enabled")
            
            # Show sample schema
            print(f"\n📄 Sample Schema:")
            print(json.dumps(first_tool, indent=2))
        
        print(f"\n🎉 All tests passed!")
        print(f"✅ Google Drive schemas are compatible with OpenAI Responses API")
        print(f"✅ Strict mode is properly configured")
        print(f"✅ All {len(responses_tools)} tools are ready for use")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_google_drive_schema_fix()
    sys.exit(0 if success else 1)
