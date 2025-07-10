#!/usr/bin/env python3
"""
Direct test of OpenAI Responses API to debug the exact error
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openai import AsyncOpenAI


async def test_responses_api_directly():
    """Test the Responses API directly with our tool format"""
    
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test tool format (simplified version of what we generate)
    test_tool = {
        "type": "function",
        "name": "test_function",
        "description": "A test function to verify tool calling works",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A test query parameter"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    }
    
    input_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Call the test_function with any query."
        },
        {
            "role": "user",
            "content": "Please call the test function with query 'hello world'"
        }
    ]
    
    print("=== Testing Responses API Direct Call ===")
    print("Tool format:")
    print(json.dumps(test_tool, indent=2))
    print()
    
    try:
        # Test with gpt-4.1-mini (known to support Responses API)
        print("Making API call to gpt-4.1-mini...")
        
        response = await client.responses.create(
            model="gpt-4.1-mini",
            input=input_messages,
            tools=[test_tool],
            tool_choice="required"
        )
        
        print("✅ API call successful!")
        print("Response:")
        print(response)
        
    except Exception as e:
        print(f"❌ API call failed with error:")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        
        # Try to get more details
        if hasattr(e, 'response'):
            print(f"HTTP status: {e.response.status_code if hasattr(e.response, 'status_code') else 'unknown'}")
            print(f"Response text: {e.response.text if hasattr(e.response, 'text') else 'unknown'}")
        
        if hasattr(e, 'body'):
            print(f"Error body: {e.body}")
        
        # Print full exception details
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_responses_api_directly())
