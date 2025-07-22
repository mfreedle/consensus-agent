#!/usr/bin/env python3
"""
Test Claude's web search capabilities via Anthropic API.
Tests real-time search, date awareness, and tool invocation.
"""

import os
from datetime import datetime

import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_claude_web_search():
    """Test Claude's web search tool capabilities."""
    
    # Initialize Claude client
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    print("🔍 Testing Claude Web Search Capabilities")
    print("=" * 50)
    
    # Test 1: Real-time web search
    print("\n📊 Test 1: Real-time stock price search")
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 3
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": "What is the current stock price of NVIDIA (NVDA) and what are the latest news about their AI chips? Please use web search to get real-time data."
                }
            ]
        )
        
        print("✅ Claude Web Search Response:")
        for content in response.content:
            if content.type == "text":
                print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
            elif content.type == "tool_use":
                print(f"🔧 Tool Used: {content.name}")
                print(f"📝 Tool Input: {content.input}")
        
    except Exception as e:
        print(f"❌ Error in web search test: {e}")
    
    # Test 2: Current events and date awareness
    print("\n📅 Test 2: Current events and date awareness")
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 2
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"What is today's date and what are the top 3 technology news stories from today? Today is {datetime.now().strftime('%Y-%m-%d')}."
                }
            ]
        )
        
        print("✅ Claude Date/News Response:")
        for content in response.content:
            if content.type == "text":
                print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
        
    except Exception as e:
        print(f"❌ Error in date/news test: {e}")
    
    # Test 3: Technical documentation search
    print("\n📚 Test 3: Latest API documentation search")
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 2
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": "Find the latest Anthropic Claude API documentation for the web search tool and summarize the key parameters and usage."
                }
            ]
        )
        
        print("✅ Claude Documentation Search Response:")
        for content in response.content:
            if content.type == "text":
                print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
        
    except Exception as e:
        print(f"❌ Error in documentation search test: {e}")
    
    # Test 4: Test without web search (for comparison)
    print("\n🚫 Test 4: Same query without web search (for comparison)")
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": "What is the current stock price of NVIDIA (NVDA)? (This test has no web search tool enabled)"
                }
            ]
        )
        
        print("✅ Claude Response (No Web Search):")
        for content in response.content:
            if content.type == "text":
                print(content.text[:300] + "..." if len(content.text) > 300 else content.text)
        
    except Exception as e:
        print(f"❌ Error in no-web-search test: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Claude Web Search Test Complete!")

if __name__ == "__main__":
    # Check if ANTHROPIC_API_KEY is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not found!")
        print("Please set your Anthropic API key in the .env file.")
        exit(1)
    
    test_claude_web_search()
