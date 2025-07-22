#!/usr/bin/env python3
"""
Test script to verify Google Drive tools fix
"""

import asyncio
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.google.service import GoogleDriveService
from app.llm.google_drive_tools import GoogleDriveTools


async def test_google_drive_tools():
    """Test that GoogleDriveTools has the required methods"""
    
    print("🔧 Testing Google Drive Tools Fix...")
    
    # Create GoogleDriveService instance (this would normally be dependency injected)
    google_service = GoogleDriveService()
    
    # Create GoogleDriveTools instance
    google_tools = GoogleDriveTools(google_service)
    
    # Test 1: Check if get_tool_definitions method exists
    if hasattr(google_tools, 'get_tool_definitions'):
        print("✅ get_tool_definitions method exists")
        
        # Test 2: Check if it returns the expected format
        try:
            tool_definitions = google_tools.get_tool_definitions()
            print(f"✅ get_tool_definitions returns {len(tool_definitions)} tools")
            
            # Test 3: Verify the structure
            if tool_definitions and isinstance(tool_definitions, list):
                first_tool = tool_definitions[0]
                if 'type' in first_tool and 'function' in first_tool:
                    print("✅ Tool definitions have correct structure")
                    print(f"   First tool: {first_tool['function']['name']}")
                else:
                    print("❌ Tool definitions have incorrect structure")
            else:
                print("❌ get_tool_definitions didn't return a list")
                
        except Exception as e:
            print(f"❌ Error calling get_tool_definitions: {e}")
    else:
        print("❌ get_tool_definitions method missing")
    
    # Test 4: Check if get_available_functions still works
    if hasattr(google_tools, 'get_available_functions'):
        try:
            functions = google_tools.get_available_functions()
            print(f"✅ get_available_functions returns {len(functions)} functions")
        except Exception as e:
            print(f"❌ Error calling get_available_functions: {e}")
    else:
        print("❌ get_available_functions method missing")
    
    print("\n🎯 Google Drive Tools Fix Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_google_drive_tools())
    asyncio.run(test_google_drive_tools())
