#!/usr/bin/env python3
"""
Test exactly what the frontend API call gets
"""

import asyncio
import json

from app.services.database_curated_models import \
    database_curated_models_service


async def test_frontend_api_call():
    """Test the exact same API call the frontend makes"""
    try:
        models = await database_curated_models_service.get_models()
        
        print(f"✅ API returned {len(models)} models")
        
        # Test the frontend filtering logic
        active_models = [m for m in models if m.get('is_active') != False]
        print(f"📊 Models where is_active != False: {len(active_models)}")
        
        if len(active_models) < len(models):
            inactive_models = [m for m in models if m.get('is_active') == False]
            print(f"⚠️  Inactive models found: {len(inactive_models)}")
            for model in inactive_models:
                print(f"   - {model['id']}: is_active = {model.get('is_active')}")
        
        # Test auto-selection logic (first 2 models)
        first_two = models[:2]
        print(f"\n🎯 First 2 models (auto-selection):")
        for i, model in enumerate(first_two):
            print(f"   {i+1}. {model['id']} - {model['display_name']} (is_active: {model.get('is_active')})")
        
        # Check provider grouping
        providers = list(set(m['provider'] for m in models))
        print(f"\n🏷️  Providers: {providers}")
        for provider in providers:
            provider_models = [m for m in models if m['provider'] == provider]
            print(f"   {provider}: {len(provider_models)} models")
        
        # Check if GPT-4.1 is in the list
        gpt_models = [m for m in models if 'gpt-4.1' in m['id']]
        print(f"\n🤖 GPT-4.1 models found: {len(gpt_models)}")
        for model in gpt_models:
            print(f"   - {model['id']}: {model['display_name']}")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_frontend_api_call())
