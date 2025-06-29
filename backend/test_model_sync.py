#!/usr/bin/env python3
"""
Test script for model sync functionality
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.database.connection import AsyncSessionLocal
from app.services.model_sync import model_sync_service


async def test_model_sync():
    """Test the model sync functionality"""
    print("Testing model sync functionality...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Test OpenAI sync (should work since we have an API key)
            print("\n--- Testing OpenAI model sync ---")
            result = await model_sync_service.fetch_openai_models(db)
            print(f"OpenAI sync result: {len(result) if result else 0} models fetched")
            if result:
                for model in result[:3]:  # Show first 3 models
                    print(f"  - {model.get('model_id', 'Unknown')}: {model.get('display_name', 'No name')}")
            
            # Test other providers (should fail gracefully without API keys)
            for provider, method in [
                ("grok", model_sync_service.fetch_grok_models),
                ("deepseek", model_sync_service.fetch_deepseek_models),
                ("anthropic", model_sync_service.fetch_anthropic_models)
            ]:
                print(f"\n--- Testing {provider} model sync ---")
                try:
                    result = await method(db)
                    print(f"{provider} sync result: {len(result) if result else 0} models fetched")
                except Exception as e:
                    print(f"{provider} sync failed (expected without API key): {e}")
            
            # Test full sync
            print("\n--- Testing full sync ---")
            result = await model_sync_service.sync_all_models(db)
            print(f"Full sync result: {result}")
            
        except Exception as e:
            print(f"Error during testing: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_model_sync())
