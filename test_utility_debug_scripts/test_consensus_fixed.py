#!/usr/bin/env python3
"""
Simple test to verify the fixed consensus engine
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

async def test_consensus_simple():
    """Test the consensus generation with a simple question"""
    print("🧠 Testing Fixed Consensus Generation...")
    
    orchestrator = LLMOrchestrator()
    test_prompt = "What are the benefits of exercise?"
    
    print(f"\n📝 Test Prompt: {test_prompt}")
    
    try:
        consensus_result = await orchestrator.generate_consensus(
            prompt=test_prompt,
            openai_model="gpt-4o-mini",
            grok_model="grok-2-latest"
        )
        
        print(f"\n✅ Consensus Generation Successful!")
        print(f"📊 Results:")
        print(f"   Final Consensus: {consensus_result.final_consensus[:300]}...")
        print(f"   Confidence Score: {consensus_result.confidence_score}")
        print(f"   Reasoning: {consensus_result.reasoning[:200]}...")
        print(f"   Debate Points: {len(consensus_result.debate_points)} points")
        
        print(f"\n🔍 Individual Response Confidences:")
        print(f"   OpenAI: {consensus_result.openai_response.confidence}")
        print(f"   Grok: {consensus_result.grok_response.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Consensus Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Consensus Engine Fix Test")
    print("=" * 40)
    
    # Check API keys
    print(f"🔑 API Keys Status:")
    print(f"   OpenAI: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
    print(f"   Grok: {'✅ Set' if settings.grok_api_key else '❌ Missing'}")
    
    if not settings.openai_api_key:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test consensus generation
    success = await test_consensus_simple()
    
    if success:
        print("\n✅ Consensus engine is now working correctly!")
    else:
        print("\n❌ Consensus engine still has issues.")

if __name__ == "__main__":
    asyncio.run(main())
