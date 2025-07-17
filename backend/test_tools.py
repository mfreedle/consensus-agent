#!/usr/bin/env python3

import asyncio
import sys

sys.path.append('.')
from app.llm.orchestrator import LLMOrchestrator


async def test_openai_tools():
    orchestrator = LLMOrchestrator()
    
    # Test with a question that should trigger web search
    prompt = 'Can you search for the latest WNBA news from this week? Today is July 16, 2025.'
    
    print('Testing OpenAI with built-in tools awareness...')
    print(f'Prompt: {prompt}')
    print('=' * 50)
    
    try:
        response = await orchestrator.get_openai_response_with_builtin_tools(prompt, 'gpt-4o-mini')
        print(f'Response: {response.content[:500]}...')
        print(f'Confidence: {response.confidence}')
        print(f'Reasoning: {response.reasoning}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(test_openai_tools())
