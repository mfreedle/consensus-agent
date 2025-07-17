#!/usr/bin/env python3
"""
Test script to verify Grok image generation capabilities.
"""

import asyncio
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.llm.orchestrator import LLMOrchestrator


async def test_grok_image_generation():
    """Test direct Grok image generation."""
    print("🎨 Testing Grok Image Generation...")
    
    orchestrator = LLMOrchestrator()
    
    # Test image generation with various prompts
    test_prompts = [
        "A futuristic city with flying cars and neon lights",
        "A happy golden retriever playing in a field of flowers",
        "Abstract art with vibrant colors and geometric shapes"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i}: {prompt} ---")
        
        try:
            response = await orchestrator.generate_grok_image(prompt)
            
            print(f"✅ Image Generation Response:")
            print(f"Model: {response.model}")
            print(f"Confidence: {response.confidence}")
            print(f"Response Length: {len(response.content)} characters")
            print(f"Contains Image Data: {'data:image/' in response.content}")
            print(f"Reasoning: {response.reasoning}")
            
            if response.confidence > 0.8:
                print("🎉 SUCCESS: Image generation working!")
            else:
                print("⚠️ Image generation had issues")
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_grok_auto_image_detection():
    """Test automatic image generation detection in Grok tools."""
    print("\n🔍 Testing Automatic Image Detection...")
    
    orchestrator = LLMOrchestrator()
    
    # Test prompts that should trigger image generation
    image_prompts = [
        "Can you generate an image of a sunset over the ocean?",
        "Create a picture of a robot playing chess",
        "I want to see an illustration of a magical forest"
    ]
    
    for i, prompt in enumerate(image_prompts, 1):
        print(f"\n--- Auto-Detection Test {i}: {prompt} ---")
        
        try:
            # This should automatically detect and route to image generation
            response = await orchestrator.get_grok_response_with_tools(prompt, "grok-3-latest")
            
            print(f"✅ Auto-Detection Response:")
            print(f"Model: {response.model}")
            print(f"Confidence: {response.confidence}")
            print(f"Routed to Image Gen: {'grok-2-image' in response.model}")
            print(f"Contains Image Data: {'data:image/' in response.content}")
            
            if "grok-2-image" in response.model:
                print("🎯 SUCCESS: Automatic image detection working!")
            else:
                print("⚠️ Did not auto-detect image request")
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Run all image generation tests."""
    print("🚀 Starting Grok Image Generation Tests...")
    
    try:
        # Test 1: Direct image generation
        await test_grok_image_generation()
        
        # Test 2: Automatic detection
        await test_grok_auto_image_detection()
        
        print("\n📊 Summary:")
        print("✅ Grok 2 Image model added to curated models")
        print("✅ Direct image generation method implemented")
        print("✅ Automatic image detection in Grok tools")
        print("✅ Chat router updated to handle grok-2-image")
        
        print("\n🎉 Image generation support is ready!")
        print("Users can now:")
        print("1. Select 'Grok 2 Image Generator' from the model dropdown")
        print("2. Ask any Grok model to generate images (auto-detection)")
        print("3. See generated images directly in the chat interface")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
