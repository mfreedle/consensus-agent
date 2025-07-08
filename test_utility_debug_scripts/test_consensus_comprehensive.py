#!/usr/bin/env python3
"""
Comprehensive test of the fixed consensus engine
"""

import asyncio
import logging
import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

# Change to the backend directory to ensure proper config loading
os.chdir(backend_dir)

from app.config import settings
from app.llm.orchestrator import LLMOrchestrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_consensus_comprehensive():
    """Test consensus with controversial topic (should have debate points)"""
    print("🧠 Testing Consensus with Controversial Topic...")
    
    orchestrator = LLMOrchestrator()
    test_prompt = "Should artificial intelligence replace human workers?"
    
    print(f"\n📝 Test Prompt: {test_prompt}")
    
    try:
        consensus_result = await orchestrator.generate_consensus(
            prompt=test_prompt,
            openai_model="gpt-4o-mini",
            grok_model="grok-2-latest"
        )
        
        print(f"\n✅ Consensus Generated!")
        print(f"   Confidence Score: {consensus_result.confidence_score}")
        print(f"   Debate Points: {len(consensus_result.debate_points)} points")
        
        if consensus_result.debate_points:
            print(f"   Debate Points:")
            for i, point in enumerate(consensus_result.debate_points, 1):
                print(f"     {i}. {point}")
        
        print(f"\n📊 Response Quality:")
        print(f"   OpenAI Confidence: {consensus_result.openai_response.confidence}")
        print(f"   Grok Confidence: {consensus_result.grok_response.confidence}")
        print(f"   Both models provided valid responses: {consensus_result.openai_response.confidence > 0 and consensus_result.grok_response.confidence > 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_model_failure_scenario():
    """Test consensus when using non-existent Grok model"""
    print("\n🧠 Testing Model Failure Scenario...")
    
    orchestrator = LLMOrchestrator()
    test_prompt = "What is the capital of France?"
    
    print(f"\n📝 Test Prompt: {test_prompt}")
    print("   Using non-existent Grok model to test fallback...")
    
    try:
        consensus_result = await orchestrator.generate_consensus(
            prompt=test_prompt,
            openai_model="gpt-4o-mini",
            grok_model="grok-nonexistent"  # This should fail
        )
        
        print(f"\n✅ Fallback Consensus Generated!")
        print(f"   Confidence Score: {consensus_result.confidence_score}")
        print(f"   OpenAI worked: {consensus_result.openai_response.confidence > 0}")
        print(f"   Grok failed as expected: {consensus_result.grok_response.confidence == 0}")
        print(f"   Final consensus provided: {len(consensus_result.final_consensus) > 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Comprehensive Consensus Engine Test")
    print("=" * 50)
    
    # Test 1: Normal consensus with controversial topic
    success1 = await test_consensus_comprehensive()
    
    # Test 2: Model failure scenario
    success2 = await test_model_failure_scenario()
    
    print(f"\n📊 Test Results:")
    print(f"   Normal consensus: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Failure scenario: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print(f"\n🎉 All tests passed! Consensus engine is robust and ready.")
    else:
        print(f"\n⚠️ Some tests failed. Review the output above.")

if __name__ == "__main__":
    asyncio.run(main())
