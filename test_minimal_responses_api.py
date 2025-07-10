#!/usr/bin/env python3
"""
Simple test to reproduce the "Missing required parameter: 'tools[0].name'" error
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.config import settings
from openai import AsyncOpenAI


async def test_minimal_tool_call():
    """Test with minimal tool to reproduce the exact error"""
    
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    # Minimal test tool exactly as shown in DataCamp guide
    minimal_tool = {
        "type": "function",
        "name": "test_function",
        "description": "A simple test function",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "A test message"
                }
            },
            "required": ["message"],
            "additionalProperties": False
        },
        "strict": True
    }
    
    print("Testing Responses API with minimal tool...")
    print(f"Tool: {minimal_tool}")
    
    try:
        response = await client.responses.create(
            model="gpt-4.1-mini",
            input="Call the test function with message 'hello world'",
            tools=[minimal_tool],
            tool_choice="auto"
        )
        
        print("✅ SUCCESS: Tool call worked!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print(f"Error type: {type(e)}")
        
        # Check if this is the specific error we're looking for
        error_str = str(e)
        if "Missing required parameter" in error_str and "tools[0].name" in error_str:
            print("🎯 FOUND THE EXACT ERROR!")
            print("This confirms the issue is with tool schema format.")
        
        return False
    
    return True

async def test_models():
    """Test which models actually work with Responses API"""
    
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    # Test without tools first
    models_to_test = ["gpt-4.1-mini", "gpt-4.1", "o3-mini", "o3", "gpt-4o"]
    
    for model in models_to_test:
        try:
            print(f"Testing {model}...")
            response = await client.responses.create(
                model=model,
                input="Hello, respond with just 'OK'"
            )
            print(f"✅ {model}: Basic call works")
            
        except Exception as e:
            print(f"❌ {model}: {e}")

if __name__ == "__main__":
    print("=== Testing OpenAI Responses API ===")
    print()
    
    # First test which models work at all
    print("1. Testing basic model availability:")
    asyncio.run(test_models())
    
    print()
    print("2. Testing tool calling:")
    success = asyncio.run(test_minimal_tool_call())
    
    if not success:
        print()
        print("🔍 Debugging suggestions:")
        print("1. Check if gpt-4.1-mini is available in your account")
        print("2. Verify OpenAI library version (should be latest)")
        print("3. Check if Responses API is enabled for your account")
