#!/usr/bin/env python3
"""
Simple Railway Database Migration Script

Uses the updated seed_models function to populate production database.
Run this after Railway deployment to ensure all models are available.
"""

import asyncio

from app.database.connection import seed_models
from app.services.database_curated_models import DatabaseCuratedModelsService


async def simple_railway_migration():
    """Simple migration using the updated seed_models function"""
    print("🚀 Starting simple Railway migration...")
    
    try:
        # Force refresh to ensure all models are seeded
        print("📦 Seeding comprehensive model set (force refresh)...")
        await seed_models(force_refresh=True)
        
        # Verify models are present
        service = DatabaseCuratedModelsService()
        models = await service.get_models()
        
        print(f"✅ Migration complete! {len(models)} models now available:")
        
        # Group by provider
        from collections import defaultdict
        by_provider = defaultdict(list)
        for model in models:
            by_provider[model.get('provider', 'unknown')].append(model.get('id', 'unknown'))
        
        for provider, model_ids in sorted(by_provider.items()):
            print(f"  📋 {provider.title()}: {len(model_ids)} models")
            for model_id in sorted(model_ids):
                print(f"    - {model_id}")
        
        # Check for Grok-4 specifically
        grok_4 = [m for m in models if m.get('id') == 'grok-4']
        if grok_4:
            print("\n🎯 Grok-4 verified with correct specs:")
            model = grok_4[0]
            print(f"  Description: {model.get('description', 'N/A')}")
            print(f"  Context window: {model.get('context_window', 'N/A')} tokens")
            caps = model.get('capabilities', {})
            print(f"  Image generation: {caps.get('image_generation', 'N/A')}")
            print(f"  Reasoning level: {caps.get('reasoning', 'N/A')}")
        
        print("\n🎉 Railway database migration successful!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(simple_railway_migration())
