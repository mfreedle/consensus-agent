#!/usr/bin/env python3
"""
Test script to verify that Grok 3 works as consensus judge and has         print("📊 Summary:")
        print(f"Web Search Works: {'✅' if web_search_response.confidence > 0.5 else '❌'}")
        print(f"Consensus Judge Works: {'✅' if consensus_response.confidence_score > 0.5 else '❌'}")
        print(f"Tools Integration Works: {'✅' if tools_response.confidence > 0.5 else '❌'}")
        
        if all([web_search_response.confidence > 0.5, consensus_response.confidence_score > 0.5, tools_response.confidence > 0.5]):
            print("\n🎉 All tests passed! Grok 3 is working as consensus judge with full tool support.")
        else:
            print("\n⚠️ Some tests failed. Check the outputs above for details.")h capabilities.
"""

import asyncio
import logging
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.llm.orchestrator import LLMOrchestrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_grok_web_search():
    """Test Grok's web search capabilities."""
    print("\n🔍 Testing Grok Web Search...")
    
    orchestrator = LLMOrchestrator()
    
    # Test current events query
    response = await orchestrator.get_grok_response_with_tools(
        "What are the latest news headlines from today? Use web search to find current international news."
    )
    
    print(f"✅ Grok Web Search Response:")
    print(f"Content: {response.content[:500]}...")
    print(f"Confidence: {response.confidence}")
    print(f"Has Citations: {'citations' in response.content.lower()}")
    print(f"Has URLs: {'http' in response.content}")
    
    return response

async def test_consensus_with_grok_judge():
    """Test consensus generation with Grok 3 as judge."""
    print("\n🤝 Testing Consensus with Grok 3 Judge...")
    
    orchestrator = LLMOrchestrator()
    
    # Test with multiple models including Grok
    test_models = [
        "gpt-4o",  # OpenAI with tools
        "grok-3-latest",  # Grok with web search
        "claude-3-5-sonnet-20241022"  # Claude with tools
    ]
    
    consensus_response = await orchestrator.generate_consensus_dynamic(
        prompt="What are the current trends in AI development for 2025? Include both technical innovations and market developments.",
        selected_models=test_models
    )
    
    print("✅ Consensus Response (Judge: Grok 3):")
    print(f"Content: {consensus_response.final_consensus[:600]}...")
    print(f"Confidence: {consensus_response.confidence_score}")
    print(f"Tool Usage: {'real-time' in consensus_response.final_consensus.lower()}")
    print(f"Synthesis Quality: {'consensus' in consensus_response.final_consensus.lower()}")
    
    return consensus_response

async def test_grok_tools_integration():
    """Test that GoogleDriveTools integration works with Grok."""
    print("\n📁 Testing Grok GoogleDriveTools Integration...")
    
    orchestrator = LLMOrchestrator()
    
    # Simple query that might trigger function calling
    response = await orchestrator.get_grok_response_with_tools(
        "Search for any documents related to 'test' or 'meeting' and summarize what you find. Also search the web for current meeting best practices."
    )
    
    print(f"✅ Grok Tools Integration Response:")
    print(f"Content: {response.content[:400]}...")
    print(f"Confidence: {response.confidence}")
    print(f"Function Calls: {'function' in str(response).lower()}")
    
    return response

async def main():
    """Run all tests."""
    print("🚀 Starting Grok Consensus Judge and Web Search Tests...")
    
    try:
        # Test 1: Grok web search
        web_search_response = await test_grok_web_search()
        
        # Test 2: Consensus with Grok judge
        consensus_response = await test_consensus_with_grok_judge()
        
        # Test 3: Grok tools integration
        tools_response = await test_grok_tools_integration()
        
        print("\n📊 Summary:")
        print(f"Web Search Works: {'✅' if web_search_response.confidence > 0.5 else '❌'}")
        print(f"Consensus Judge Works: {'✅' if consensus_response.confidence_score > 0.5 else '❌'}")
        print(f"Tools Integration Works: {'✅' if tools_response.confidence > 0.5 else '❌'}")
        
        if all([web_search_response.confidence > 0.5, consensus_response.confidence_score > 0.5, tools_response.confidence > 0.5]):
            print("\n🎉 All tests passed! Grok 3 is working as consensus judge with full tool support.")
        else:
            print("\n⚠️ Some tests failed. Check the outputs above for details.")
            
    except Exception as e:
        logger.error(f"Test execution error: {e}")
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
