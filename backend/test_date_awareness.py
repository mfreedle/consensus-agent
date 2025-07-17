#!/usr/bin/env python3

import asyncio
import sys
from datetime import datetime

sys.path.append('.')
from app.llm.orchestrator import LLMOrchestrator


async def test_date_awareness():
    """Test that all provider methods include current date in their prompts"""
    orchestrator = LLMOrchestrator()
    
    # Simple prompt to test date awareness
    prompt = "What is today's date?"
    
    print(f"Testing date awareness across all providers...")
    print(f"Expected date: {datetime.now().strftime('%B %d, %Y')}")
    print('=' * 60)
    
    # Test OpenAI
    print("Testing OpenAI date awareness...")
    try:
        response = await orchestrator.get_openai_response_with_builtin_tools(prompt, 'gpt-4o-mini')
        print(f"OpenAI Response: {response.content[:200]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"OpenAI Error: {e}\n")

    # Test Grok
    print("Testing Grok date awareness...")
    try:
        response = await orchestrator.get_grok_response_with_tools(prompt, 'grok-2-1212')
        print(f"Grok Response: {response.content[:200]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"Grok Error: {e}\n")

    # Test Claude
    print("Testing Claude date awareness...")
    try:
        response = await orchestrator.get_claude_response_with_tools(prompt, 'claude-3-5-sonnet-20241022')
        print(f"Claude Response: {response.content[:200]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"Claude Error: {e}\n")

    # Test DeepSeek
    print("Testing DeepSeek date awareness...")
    try:
        response = await orchestrator.get_deepseek_response_with_tools(prompt, 'deepseek-chat')
        print(f"DeepSeek Response: {response.content[:200]}...")
        print(f"Confidence: {response.confidence}")
        print()
    except Exception as e:
        print(f"DeepSeek Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(test_date_awareness())
