#!/usr/bin/env python3

import asyncio
import sys

from openai import AsyncOpenAI

sys.path.append('.')
from app.config import settings


async def test_minimal_web_search():
    """Minimal test of OpenAI Responses API with web search"""
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    try:
        print("Testing minimal web search with Responses API...")
        
        # Try the most basic web search configuration
        response = await client.responses.create(
            model="gpt-4o-mini",
            input="What is today's date and what's happening in the WNBA this week?",
            tools=[{"type": "web_search"}]  # type: ignore
        )
        
        print("Success! Response:")
        if hasattr(response, 'output'):
            print(response.output)
        else:
            print(response)
            
    except Exception as e:
        print(f"Error: {e}")
        
        # Try without tools
        print("\nTrying without tools...")
        try:
            response = await client.responses.create(
                model="gpt-4o-mini",
                input="What is today's date? (Note: Today is July 16, 2025)"
            )
            print("No-tools response:")
            if hasattr(response, 'output'):
                print(response.output)
            else:
                print(response)
        except Exception as e2:
            print(f"Even basic response failed: {e2}")

if __name__ == "__main__":
    asyncio.run(test_minimal_web_search())
