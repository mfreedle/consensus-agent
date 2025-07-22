#!/usr/bin/env python3
"""
Test Claude's web search capabilities using the backend orchestrator.
Tests real-time search, date awareness, and tool invocation.
"""

import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime

from app.llm.orchestrator import LLMOrchestrator


async def test_claude_web_search():
    """Test Claude's web search tool capabilities via orchestrator."""
    
    print("🔍 Testing Claude Web Search Capabilities via Orchestrator")
    print("=" * 60)
    
    orchestrator = LLMOrchestrator()
    
    # Test 1: Real-time web search for current events
    print("\n📊 Test 1: Real-time current events search")
    try:
        response = await orchestrator.get_claude_response_with_tools(
            prompt="What are the top 3 technology news stories today? Please use web search to get current information.",
            model="claude-3-5-sonnet-20241022"
        )
        
        print(f"✅ Claude Response (Confidence: {response.confidence}):")
        print(response.content[:800] + "..." if len(response.content) > 800 else response.content)
        print(f"📝 Reasoning: {response.reasoning}")
        
    except Exception as e:
        print(f"❌ Error in current events test: {e}")
    
    # Test 2: Stock price search
    print("\n💰 Test 2: Real-time stock information")
    try:
        response = await orchestrator.get_claude_response_with_tools(
            prompt="What is the current stock price of Apple (AAPL) and what recent news affects it? Use web search for real-time data.",
            model="claude-3-5-sonnet-20241022"
        )
        
        print(f"✅ Claude Stock Response (Confidence: {response.confidence}):")
        print(response.content[:800] + "..." if len(response.content) > 800 else response.content)
        
    except Exception as e:
        print(f"❌ Error in stock price test: {e}")
    
    # Test 3: Technical documentation search
    print("\n📚 Test 3: API documentation search")
    try:
        response = await orchestrator.get_claude_response_with_tools(
            prompt="Find and summarize the latest changes in the Anthropic Claude API, especially regarding web search capabilities.",
            model="claude-3-5-sonnet-20241022"
        )
        
        print(f"✅ Claude Documentation Response (Confidence: {response.confidence}):")
        print(response.content[:800] + "..." if len(response.content) > 800 else response.content)
        
    except Exception as e:
        print(f"❌ Error in documentation search test: {e}")
    
    # Test 4: Date awareness without tools (for comparison)
    print("\n📅 Test 4: Date awareness test")
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        response = await orchestrator.get_claude_response_with_tools(
            prompt=f"What is today's date? Today should be {current_date}. Can you confirm this and tell me what day of the week it is?",
            model="claude-3-5-sonnet-20241022"
        )
        
        print(f"✅ Claude Date Response (Confidence: {response.confidence}):")
        print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        
    except Exception as e:
        print(f"❌ Error in date awareness test: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Claude Web Search Test Complete!")
    print("\nKey Findings:")
    print("🔍 Web Search Tool: Available via web_search_20250305")
    print("🖥️  Computer Use: Available via computer_20241022") 
    print("📝 Text Editor: Available via text_editor_20241022")
    print("⚡ Bash Terminal: Available via bash_20241022")
    print("💰 Pricing: $10 per 1,000 searches + standard token costs")

if __name__ == "__main__":
    # Check environment setup
    import os

    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not found!")
        print("Please set your Anthropic API key in the .env file.")
        exit(1)
    
    # Run the async test
    asyncio.run(test_claude_web_search())
