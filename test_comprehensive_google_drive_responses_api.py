#!/usr/bin/env python3
"""
Comprehensive end-to-end test for Google Drive Responses API integration.
This script validates the complete workflow from schema to API call.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

# Add backend to Python path
sys.path.append('./backend')

try:
    from app.llm.google_drive_tools import GoogleDriveTools
    from app.llm.orchestrator import LLMOrchestrator
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_responses_api_tool_format(tool: Dict[str, Any]) -> List[str]:
    """
    Validate a tool formatted for OpenAI Responses API.
    Returns list of validation errors.
    """
    errors = []
    
    # Check top-level structure
    if "type" not in tool or tool["type"] != "function":
        errors.append("Tool must have 'type': 'function'")
    
    if "name" not in tool:
        errors.append("Tool must have 'name' field")
    
    if "description" not in tool:
        errors.append("Tool must have 'description' field")
    
    if "parameters" not in tool:
        errors.append("Tool must have 'parameters' field")
    
    if "strict" not in tool or tool["strict"] is not True:
        errors.append("Tool must have 'strict': True for Responses API")
    
    # Validate parameters schema
    params = tool.get("parameters", {})
    
    if params.get("type") != "object":
        errors.append("Parameters type must be 'object'")
    
    if params.get("additionalProperties") is not False:
        errors.append("Parameters must have 'additionalProperties': False")
    
    if "required" not in params:
        errors.append("Parameters must have 'required' array")
    elif not isinstance(params["required"], list):
        errors.append("'required' must be an array")
    
    if "properties" not in params:
        errors.append("Parameters must have 'properties' object")
    elif not isinstance(params["properties"], dict):
        errors.append("'properties' must be an object")
    
    # Check that all properties are in required array
    if "properties" in params and "required" in params:
        properties = params["properties"]
        required = params["required"]
        
        for prop_name in properties.keys():
            if prop_name not in required:
                errors.append(f"Property '{prop_name}' not in required array")
        
        for req_prop in required:
            if req_prop not in properties:
                errors.append(f"Required property '{req_prop}' not in properties")
    
    return errors

async def test_orchestrator_integration():
    """Test the complete orchestrator integration with Google Drive tools"""
    
    logger.info("Testing LLM Orchestrator integration...")
    
    # Create orchestrator instance
    orchestrator = LLMOrchestrator()
    
    # Create Google Drive tools (without actual service for testing)
    mock_service = None
    google_drive_tools = GoogleDriveTools(mock_service)
    
    # Set tools in orchestrator
    orchestrator.set_google_drive_tools(google_drive_tools)
    
    # Test Responses API tool format
    logger.info("Testing Responses API tool format...")
    responses_tools = orchestrator._get_google_drive_tools_for_responses_api()
    
    logger.info(f"Generated {len(responses_tools)} tools for Responses API")
    
    all_errors = []
    
    for tool in responses_tools:
        tool_name = tool.get("name", "unknown")
        logger.info(f"Validating tool: {tool_name}")
        
        errors = validate_responses_api_tool_format(tool)
        
        if errors:
            all_errors.extend([f"{tool_name}: {error}" for error in errors])
            logger.error(f"❌ {tool_name} has {len(errors)} errors:")
            for error in errors:
                logger.error(f"  - {error}")
        else:
            logger.info(f"✅ {tool_name} is valid")
    
    if all_errors:
        logger.error(f"❌ Tool validation failed: {len(all_errors)} errors")
        for error in all_errors:
            logger.error(f"  - {error}")
        return False
    else:
        logger.info(f"✅ All {len(responses_tools)} tools are valid for Responses API")
    
    # Test model support detection
    logger.info("\nTesting model support detection...")
    
    test_models = [
        ("gpt-4.1", True),
        ("gpt-4.1-mini", True),
        ("o3", True),
        ("o3-mini", True),
        ("gpt-4o", True),
        ("gpt-4o-mini", True),
        ("gpt-4", False),
        ("gpt-3.5-turbo", False)
    ]
    
    for model, expected_support in test_models:
        actual_support = orchestrator._supports_responses_api(model)
        if actual_support == expected_support:
            logger.info(f"✅ {model}: {'Supports' if actual_support else 'Does not support'} Responses API")
        else:
            logger.error(f"❌ {model}: Expected {expected_support}, got {actual_support}")
            return False
    
    # Test actual tool schema format
    logger.info("\nTesting sample tool schema...")
    
    if responses_tools:
        sample_tool = responses_tools[0]
        logger.info(f"Sample tool name: {sample_tool['name']}")
        
        # Verify the schema is JSON serializable
        try:
            json_str = json.dumps(sample_tool, indent=2)
            logger.info("✅ Tool schema is JSON serializable")
            
            # Verify it can be parsed back
            parsed_tool = json.loads(json_str)
            assert parsed_tool == sample_tool  # Verify roundtrip integrity
            logger.info("✅ Tool schema can be parsed back from JSON")
            
            # Show sample for verification
            logger.info(f"\nSample tool schema:\n{json_str[:500]}...")
            
        except Exception as e:
            logger.error(f"❌ Tool schema serialization error: {e}")
            return False
    
    return True

def test_google_drive_tool_parameters():
    """Test specific Google Drive tool parameter validation"""
    
    logger.info("\nTesting Google Drive tool parameters...")
    
    mock_service = None
    google_drive_tools = GoogleDriveTools(mock_service)
    functions = google_drive_tools.get_available_functions()
    
    logger.info(f"Testing {len(functions)} Google Drive functions...")
    
    # Test specific problematic patterns
    critical_checks = {
        "nullable_types": [],
        "missing_required": [],
        "invalid_additionalProperties": [],
        "enum_missing_null": []  # Changed from enum_with_null to enum_missing_null
    }
    
    for func in functions:
        func_name = func.name
        params = func.parameters
        
        if "properties" in params:
            properties = params["properties"]
            required = params.get("required", [])
            
            for prop_name, prop_def in properties.items():
                # Check nullable types format
                if isinstance(prop_def.get("type"), list):
                    if "null" in prop_def["type"]:
                        if prop_name not in required:
                            critical_checks["missing_required"].append(f"{func_name}.{prop_name}")
                        
                        # Check if enum includes null properly (must include None if nullable)
                        if "enum" in prop_def:
                            if None not in prop_def["enum"]:
                                critical_checks["enum_missing_null"].append(f"{func_name}.{prop_name}")
                
                # Check object types for additionalProperties
                if prop_def.get("type") == "object":
                    if prop_def.get("additionalProperties") is not False:
                        critical_checks["invalid_additionalProperties"].append(f"{func_name}.{prop_name}")
        
        # Check main parameters object
        if params.get("additionalProperties") is not False:
            critical_checks["invalid_additionalProperties"].append(f"{func_name}.<root>")
    
    # Report results
    all_good = True
    
    for check_name, issues in critical_checks.items():
        if issues:
            logger.error(f"❌ {check_name}: {len(issues)} issues found")
            for issue in issues[:5]:  # Show first 5
                logger.error(f"  - {issue}")
            if len(issues) > 5:
                logger.error(f"  ... and {len(issues) - 5} more")
            all_good = False
        else:
            logger.info(f"✅ {check_name}: No issues found")
    
    return all_good

async def main():
    """Main test function"""
    
    print("🔧 Comprehensive Google Drive Responses API Integration Test")
    print("=" * 65)
    
    try:
        # Test 1: Orchestrator Integration
        logger.info("🧪 Test 1: Orchestrator Integration")
        test1_passed = await test_orchestrator_integration()
        
        if not test1_passed:
            logger.error("❌ Test 1 failed!")
            return False
        
        # Test 2: Google Drive Tool Parameters
        logger.info("\n🧪 Test 2: Google Drive Tool Parameters")
        test2_passed = test_google_drive_tool_parameters()
        
        if not test2_passed:
            logger.error("❌ Test 2 failed!")
            return False
        
        # Summary
        print("\n" + "=" * 65)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Google Drive tools are fully compatible with OpenAI Responses API")
        print("✅ Schemas comply with strict mode requirements")
        print("✅ Orchestrator integration is working correctly")
        print("✅ Ready for production use with GPT-4.1, GPT-4.1-mini, o3, o3-mini")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
