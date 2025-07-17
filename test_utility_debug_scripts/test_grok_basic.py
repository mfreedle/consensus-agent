#!/usr/bin/env python3
"""
Simple test to check if Grok API credentials are working.
"""

import asyncio
import os
import sys

import httpx

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.config import Settings


async def test_grok_basic():
    """Test basic Grok API connectivity."""
    print("🔍 Testing Grok API Connectivity...")
    
    settings = Settings()
    
    print(f"Grok API Key configured: {'✅ Yes' if settings.grok_api_key else '❌ No'}")
    
    if not settings.grok_api_key:
        print("❌ Grok API key is not configured. Please set the GROK_API_KEY environment variable.")
        return False
    
    # Test basic API call
    headers = {
        "Authorization": f"Bearer {settings.grok_api_key}",
        "Content-Type": "application/json"
    }
    
    request_data = {
        "model": "grok-3-latest",
        "messages": [
            {"role": "user", "content": "Say hello and tell me what you can do."}
        ],
        "max_tokens": 100
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=request_data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data["choices"][0]["message"]["content"]
                print(f"✅ Grok API working! Response: {message[:100]}...")
                return True
            else:
                print(f"❌ Grok API error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def main():
    success = await test_grok_basic()
    if success:
        print("\n🎉 Grok API is ready for consensus judge testing!")
    else:
        print("\n⚠️ Fix Grok API configuration before running consensus tests.")

if __name__ == "__main__":
    asyncio.run(main())
