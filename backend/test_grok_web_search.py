#!/usr/bin/env python3

import asyncio
import sys

sys.path.append('.')
from app.llm.orchestrator import LLMOrchestrator


async def test_grok_web_search():
    """Test Grok's Live Search capabilities"""
    orchestrator = LLMOrchestrator()
    
    print("Testing Grok Live Search capabilities...")
    print("=" * 60)
    
    # Test 1: Current Events
    print("🌐 TEST 1: Grok Web Search - Current Events")
    try:
        response = await orchestrator.get_grok_response_with_tools(
            "What's the latest news about the WNBA All-Star Game 2025? Today is July 17, 2025.", 
            'grok-2-1212'
        )
        print(f"✅ Grok Web Search Response: {response.content[:300]}...")
        print(f"Confidence: {response.confidence}")
        print(f"Reasoning: {response.reasoning}")
        print()
    except Exception as e:
        print(f"❌ Grok Web Search Error: {e}\n")

    # Test 2: X/Twitter Integration
    print("📱 TEST 2: Grok X/Twitter Search")
    try:
        response = await orchestrator.get_grok_response_with_tools(
            "What are people saying on X/Twitter about Grok AI recently?", 
            'grok-2-1212'
        )
        print(f"✅ Grok X Search Response: {response.content[:300]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"❌ Grok X Search Error: {e}\n")

    # Test 3: Current Date Awareness
    print("📅 TEST 3: Grok Date Awareness")
    try:
        response = await orchestrator.get_grok_response_with_tools(
            "What is today's date and what major events are happening this week?", 
            'grok-2-1212'
        )
        print(f"✅ Grok Date Response: {response.content[:300]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"❌ Grok Date Error: {e}\n")

    print("=" * 60)
    print("Grok testing complete!")


if __name__ == "__main__":
    asyncio.run(test_grok_web_search())
