#!/usr/bin/env python3
"""
Simple diagnostic test for Grok image generation.
"""

import asyncio
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.llm.orchestrator import LLMOrchestrator


async def test_single_image():
    """Test a single image generation."""
    print("🔧 Testing Single Image Generation (Diagnostic)...")
    
    orchestrator = LLMOrchestrator()
    
    try:
        # Simple test
        response = await orchestrator.generate_grok_image("A simple red circle")
        
        print(f"Response model: {response.model}")
        print(f"Response confidence: {response.confidence}")
        print(f"Response content preview: {response.content[:200]}...")
        print(f"Response reasoning: {response.reasoning}")
        
        if response.confidence > 0.8:
            print("✅ SUCCESS!")
        else:
            print("❌ Failed")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_image())
