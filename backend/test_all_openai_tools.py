#!/usr/bin/env python3

import asyncio
import sys

sys.path.append('.')
from app.llm.orchestrator import LLMOrchestrator


async def test_all_openai_tools():
    """Test all OpenAI tools: web search and code interpreter"""
    orchestrator = LLMOrchestrator()
    
    print("Testing OpenAI Responses API with official tools configuration...")
    print("=" * 70)
    
    # Test 1: Web Search
    print("🔍 TEST 1: Web Search")
    try:
        response = await orchestrator.get_openai_response_with_builtin_tools(
            "What's the latest news about the WNBA All-Star Game 2025?", 
            'gpt-4o-mini'
        )
        print(f"✅ Web Search Response: {response.content[:200]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"❌ Web Search Error: {e}\n")

    # Test 2: Code Interpreter
    print("🧮 TEST 2: Code Interpreter")
    try:
        response = await orchestrator.get_openai_response_with_builtin_tools(
            "Calculate the square root of 2025 and show me the calculation steps using Python code", 
            'gpt-4o-mini'
        )
        print(f"✅ Code Interpreter Response: {response.content[:300]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"❌ Code Interpreter Error: {e}\n")

    # Test 3: Current Date Awareness
    print("📅 TEST 3: Current Date Awareness")
    try:
        response = await orchestrator.get_openai_response_with_builtin_tools(
            "What is today's date and what day of the week is it?", 
            'gpt-4o-mini'
        )
        print(f"✅ Date Awareness Response: {response.content[:200]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"❌ Date Awareness Error: {e}\n")

    print("=" * 70)
    print("Testing complete!")


if __name__ == "__main__":
    asyncio.run(test_all_openai_tools())
