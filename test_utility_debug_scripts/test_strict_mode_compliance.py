#!/usr/bin/env python3
"""
Test script to verify additionalProperties: false is properly added for strict mode
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


def test_strict_mode_compliance():
    """Test that the Responses API tools have proper strict mode compliance"""
    
    print("🔒 Testing Strict Mode Compliance")
    print("=" * 50)
    
    try:
        # Initialize Google Drive tools
        google_drive_service = GoogleDriveService(settings)
        google_drive_tools = GoogleDriveTools(google_drive_service)
        llm_orchestrator.set_google_drive_tools(google_drive_tools)
        
        # Get Responses API tools
        responses_tools = llm_orchestrator._get_google_drive_tools_for_responses_api()
        
        if not responses_tools:
            print("❌ No Responses API tools found")
            return
        
        print(f"✅ Found {len(responses_tools)} tools for testing")
        
        # Test each tool for strict mode compliance
        compliant_count = 0
        
        for i, tool in enumerate(responses_tools[:3]):  # Test first 3 tools
            tool_name = tool.get('name', f'Tool {i+1}')
            print(f"\n📝 Testing Tool: {tool_name}")
            print("-" * 30)
            
            # Check if tool has strict field
            has_strict = tool.get('strict', False)
            print(f"✅ Has 'strict': {has_strict}")
            
            # Check parameters structure
            parameters = tool.get('parameters', {})
            if parameters and isinstance(parameters, dict):
                
                # Check root level additionalProperties
                has_root_additional = 'additionalProperties' in parameters
                root_additional_value = parameters.get('additionalProperties')
                print(f"✅ Root additionalProperties: {root_additional_value} (present: {has_root_additional})")
                
                # Check properties level
                properties = parameters.get('properties', {})
                if properties:
                    object_props = []
                    for prop_name, prop_def in properties.items():
                        if isinstance(prop_def, dict) and prop_def.get('type') == 'object':
                            object_props.append(prop_name)
                            has_prop_additional = 'additionalProperties' in prop_def
                            prop_additional_value = prop_def.get('additionalProperties')
                            print(f"  ✅ Property '{prop_name}' additionalProperties: {prop_additional_value} (present: {has_prop_additional})")
                    
                    if not object_props:
                        print("  ℹ️  No nested object properties found")
                
                # Check compliance
                is_compliant = (
                    has_strict and 
                    has_root_additional and 
                    root_additional_value is False
                )
                
                if is_compliant:
                    compliant_count += 1
                    print(f"🎉 Tool '{tool_name}' is COMPLIANT")
                else:
                    print(f"❌ Tool '{tool_name}' is NOT COMPLIANT")
                    
                # Show sample of full tool
                print(f"📄 Sample structure:")
                sample = {k: v for k, v in tool.items() if k != 'parameters'}
                sample['parameters'] = {k: v for k, v in parameters.items() if k != 'properties'}
                if 'properties' in parameters:
                    sample['parameters']['properties'] = f"... {len(properties)} properties ..."
                print(json.dumps(sample, indent=2))
            
            else:
                print("❌ No valid parameters found")
        
        # Summary
        print(f"\n📊 Summary")
        print("-" * 20)
        tested_count = min(3, len(responses_tools))
        print(f"✅ Tools tested: {tested_count}")
        print(f"✅ Compliant tools: {compliant_count}")
        print(f"✅ Compliance rate: {compliant_count/tested_count*100:.1f}%")
        
        if compliant_count == tested_count:
            print("🎉 ALL TOOLS ARE STRICT MODE COMPLIANT!")
        else:
            print(f"⚠️  {tested_count - compliant_count} tools need compliance fixes")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_strict_mode_compliance()
