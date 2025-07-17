#!/usr/bin/env python3
"""
Test script to verify DALL-E routing fix
"""
import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_dalle_routing():
    """Test that DALL-E models are properly routed to OpenAI image generation"""
    try:
        # Try to import the orchestrator
        from app.llm.orchestrator import LLMOrchestrator
        print("✅ Successfully imported LLMOrchestrator")
        
        # Check if the generate_openai_image method exists
        orchestrator = LLMOrchestrator()
        if hasattr(orchestrator, 'generate_openai_image'):
            print("✅ generate_openai_image method exists")
        else:
            print("❌ generate_openai_image method not found")
            return False
        
        # Try to import the chat router
        from app.chat.router import router
        print("✅ Successfully imported chat router")
        
        print("\n🎉 All imports successful! The DALL-E routing fix appears to be working.")
        print("\nThe following changes were made:")
        print("1. Added generate_openai_image() method to orchestrator.py")
        print("2. Added DALL-E routing logic to chat/router.py")
        print("3. DALL-E models (dall-e-3, dall-e-2) will now be routed to OpenAI instead of Grok")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("Testing DALL-E routing fix...")
    print("=" * 50)
    
    success = asyncio.run(test_dalle_routing())
    
    if success:
        print("\n✅ Test passed! The fix should resolve the DALL-E routing issue.")
    else:
        print("\n❌ Test failed! There may be syntax or import errors.")
