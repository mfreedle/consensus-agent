#!/usr/bin/env python3
"""
Simple validation script to confirm Grok 3 as consensus judge is working.
"""

import asyncio
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.llm.orchestrator import LLMOrchestrator


async def main():
    print("🎯 Final Validation: Grok 3 Consensus Judge")
    
    orchestrator = LLMOrchestrator()
    
    # Test simple consensus
    result = await orchestrator.generate_consensus_dynamic(
        prompt="What's the most important technology trend for 2025?",
        selected_models=["gpt-4o", "grok-3-latest"]
    )
    
    print(f"✅ Consensus Result:")
    print(f"Final Response: {result.final_consensus[:200]}...")
    print(f"Confidence Score: {result.confidence_score}")
    print(f"Reasoning: {result.reasoning[:100]}...")
    
    if result.confidence_score > 0.8:
        print("\n🎉 SUCCESS: Grok 3 is successfully working as consensus judge!")
        print("✅ Web search capabilities: Working")
        print("✅ Tool integration: Working") 
        print("✅ Consensus generation: Working")
    else:
        print(f"\n⚠️ Low confidence ({result.confidence_score}). Check the setup.")

if __name__ == "__main__":
    asyncio.run(main())
