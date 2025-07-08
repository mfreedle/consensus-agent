#!/usr/bin/env python3
"""
Debug script to test the consensus engine and identify Issues
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
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_individual_models():
    """Test individual model responses"""
    print("🔍 Testing Individual Models...")
    
    orchestrator = LLMOrchestrator()
    test_prompt = "What is quantum computing in simple terms?"
    
    print(f"\n📝 Test Prompt: {test_prompt}")
    
    # Test OpenAI response
    print("\n🤖 Testing OpenAI...")
    try:
        openai_response = await orchestrator.get_openai_response(
            prompt=test_prompt,
            model="gpt-4o-mini"  # Use a known working model
        )
        print(f"✅ OpenAI Response:")
        print(f"   Model: {openai_response.model}")
        print(f"   Content: {openai_response.content[:200]}...")
        print(f"   Confidence: {openai_response.confidence}")
        print(f"   Reasoning: {openai_response.reasoning[:100]}...")
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return False
    
    # Test Grok response
    print("\n🚀 Testing Grok...")
    try:
        grok_response = await orchestrator.get_grok_response(
            prompt=test_prompt,
            model="grok-2-latest"  # Use the correct working Grok model name
        )
        print(f"✅ Grok Response:")
        print(f"   Model: {grok_response.model}")
        print(f"   Content: {grok_response.content[:200]}...")
        print(f"   Confidence: {grok_response.confidence}")
        print(f"   Reasoning: {grok_response.reasoning[:100]}...")
    except Exception as e:
        print(f"❌ Grok Error: {e}")
        # Don't return False yet - continue to test consensus even if Grok fails
    
    return True

async def test_consensus_generation():
    """Test the full consensus generation process"""
    print("\n🧠 Testing Consensus Generation...")
    
    orchestrator = LLMOrchestrator()
    test_prompt = "What are the pros and cons of artificial intelligence?"
    
    print(f"\n📝 Test Prompt: {test_prompt}")
    
    try:
        consensus_result = await orchestrator.generate_consensus(
            prompt=test_prompt,
            openai_model="gpt-4o-mini",  # Use working models
            grok_model="grok-2-latest"
        )
        
        print(f"✅ Consensus Generation Successful!")
        print(f"📊 Results:")
        print(f"   Final Consensus: {consensus_result.final_consensus[:300]}...")
        print(f"   Confidence Score: {consensus_result.confidence_score}")
        print(f"   Reasoning: {consensus_result.reasoning[:200]}...")
        print(f"   Debate Points: {len(consensus_result.debate_points)} points")
        
        print(f"\n🔍 Individual Responses:")
        print(f"   OpenAI: {consensus_result.openai_response.content[:150]}...")
        print(f"   Grok: {consensus_result.grok_response.content[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Consensus Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_model_names():
    """Test various model names to find what works"""
    print("\n🔧 Testing Model Names...")
    
    orchestrator = LLMOrchestrator()
    test_prompt = "Hello world"
    
    # Test OpenAI models
    openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    for model in openai_models:
        try:
            response = await orchestrator.get_openai_response(test_prompt, model)
            print(f"✅ OpenAI {model}: Working")
        except Exception as e:
            print(f"❌ OpenAI {model}: {str(e)[:100]}")
    
    # Test Grok models
    grok_models = ["grok-beta", "grok-2", "grok-2-latest", "grok-3", "grok-3-latest"]
    for model in grok_models:
        try:
            response = await orchestrator.get_grok_response(test_prompt, model)
            print(f"✅ Grok {model}: Working")
        except Exception as e:
            print(f"❌ Grok {model}: {str(e)[:100]}")

async def main():
    """Main test function"""
    print("🚀 Consensus Engine Debug Script")
    print("=" * 50)
    
    # Check API keys
    print(f"🔑 API Keys Status:")
    print(f"   OpenAI: {'✅ Set' if settings.openai_api_key else '❌ Missing'}")
    print(f"   Grok: {'✅ Set' if settings.grok_api_key else '❌ Missing'}")
    
    if not settings.openai_api_key:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test individual models
    models_working = await test_individual_models()
    if not models_working:
        print("❌ Individual model testing failed. Cannot proceed with consensus testing.")
        return
    
    # Test consensus generation
    await test_consensus_generation()
    
    # Test model names
    await test_model_names()
    
    print("\n✅ Debug script completed!")

if __name__ == "__main__":
    asyncio.run(main())
