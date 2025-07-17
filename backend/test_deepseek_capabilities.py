#!/usr/bin/env python3

import asyncio
import sys

sys.path.append('.')
from app.llm.orchestrator import LLMOrchestrator


async def test_deepseek_capabilities():
    """Test DeepSeek's capabilities and check for web search"""
    orchestrator = LLMOrchestrator()
    
    print("Testing DeepSeek capabilities...")
    print("=" * 60)
    
    # Test 1: Current Events (should fail without web search)
    print("🌐 TEST 1: DeepSeek Current Events Test")
    try:
        response = await orchestrator.get_deepseek_response_with_tools(
            "What's the latest news about the WNBA All-Star Game 2025? Today is July 17, 2025.", 
            'deepseek-chat'
        )
        print(f"✅ DeepSeek Response: {response.content[:300]}...")
        print(f"Confidence: {response.confidence}")
        print(f"Reasoning: {response.reasoning}")
        print()
    except Exception as e:
        print(f"❌ DeepSeek Error: {e}\n")

    # Test 2: Mathematical Reasoning (should work well)
    print("🧮 TEST 2: DeepSeek Mathematical Reasoning")
    try:
        response = await orchestrator.get_deepseek_response_with_tools(
            "Calculate the square root of 2025 and explain your reasoning step by step", 
            'deepseek-chat'
        )
        print(f"✅ DeepSeek Math Response: {response.content[:300]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"❌ DeepSeek Math Error: {e}\n")

    # Test 3: Date Awareness
    print("📅 TEST 3: DeepSeek Date Awareness")
    try:
        response = await orchestrator.get_deepseek_response_with_tools(
            "What is today's date and what capabilities do you have?", 
            'deepseek-chat'
        )
        print(f"✅ DeepSeek Date Response: {response.content[:300]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"❌ DeepSeek Date Error: {e}\n")

    print("=" * 60)
    print("DeepSeek testing complete!")
    print("\nExpected Results:")
    print("- ❌ Current Events: Should fail (no web search)")
    print("- ✅ Math Reasoning: Should work well")
    print("- ✅ Date Awareness: Should work with provided date")


if __name__ == "__main__":
    asyncio.run(test_deepseek_capabilities())
