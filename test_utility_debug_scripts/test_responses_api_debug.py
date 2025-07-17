#!/usr/bin/env python3
"""
Test script to verify the exact tool format being sent to OpenAI Responses API
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.google.service import GoogleDriveService
from backend.app.llm.google_drive_tools import GoogleDriveTools
from backend.app.llm.orchestrator import LLMOrchestrator


# Mock settings for testing
class MockSettings:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "test-key")
        self.openai_org_id = None
        self.grok_api_key = "test-grok-key"

# Mock user for testing
class MockUser:
    def __init__(self):
        self.id = "test-user-id"
        self.email = "test@example.com"

async def test_responses_api_tool_format():
    """Test the tool format being sent to OpenAI Responses API"""
    
    # Setup
    settings = MockSettings()
    mock_user = MockUser()
    
    # Initialize orchestrator
    orchestrator = LLMOrchestrator()
    
    # Setup Google Drive tools (minimal mock)
    google_service = GoogleDriveService(settings)
    google_drive_tools = GoogleDriveTools(google_service)
    orchestrator.set_google_drive_tools(google_drive_tools)
    
    # Get tools for Responses API
    tools = orchestrator._get_google_drive_tools_for_responses_api()
    
    print("=== OpenAI Responses API Tool Format ===")
    print(f"Number of tools: {len(tools)}")
    print()
    
    for i, tool in enumerate(tools):
        print(f"Tool {i + 1}: {tool['name']}")
        print("Schema:")
        print(json.dumps(tool, indent=2))
        print()
    
    # Test the exact API call parameters
    input_messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant with access to Google Drive. You can read, edit, create, copy, move, and manage Google Drive files when requested by the user."
        },
        {
            "role": "user",
            "content": "Search for files in my Google Drive that contain 'test' in the name."
        }
    ]
    
    # Build API call parameters (what would be sent to OpenAI)
    api_params = {
        "model": "gpt-4.1-mini",
        "input": input_messages,
        "tools": tools,
        "tool_choice": "required"
    }
    
    print("=== API Call Parameters ===")
    print("Model:", api_params["model"])
    print("Input messages:", len(api_params["input"]))
    print("Tools:", len(api_params["tools"]))
    print("Tool choice:", api_params["tool_choice"])
    print()
    
    print("=== Full API Call JSON ===")
    print(json.dumps(api_params, indent=2))
    
    # Validate tool schema according to OpenAPI spec
    print("\n=== Tool Schema Validation ===")
    for tool in tools:
        required_fields = ["type", "name", "parameters", "strict"]
        missing_fields = [field for field in required_fields if field not in tool]
        
        if missing_fields:
            print(f"❌ Tool '{tool.get('name', 'UNKNOWN')}' missing required fields: {missing_fields}")
        else:
            print(f"✅ Tool '{tool['name']}' has all required fields")
            
            # Check field types
            if tool["type"] != "function":
                print(f"   ❌ 'type' should be 'function', got '{tool['type']}'")
            
            if not isinstance(tool["name"], str):
                print(f"   ❌ 'name' should be string, got {type(tool['name'])}")
            
            if tool["parameters"] is not None and not isinstance(tool["parameters"], dict):
                print(f"   ❌ 'parameters' should be dict or null, got {type(tool['parameters'])}")
            
            if not isinstance(tool["strict"], bool):
                print(f"   ❌ 'strict' should be boolean, got {type(tool['strict'])}")

if __name__ == "__main__":
    asyncio.run(test_responses_api_tool_format())
