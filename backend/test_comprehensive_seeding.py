#!/usr/bin/env python3
"""Test script to verify comprehensive model seeding with Grok-4"""

import asyncio
from collections import Counter

from app.database.connection import seed_models
from app.services.database_curated_models import DatabaseCuratedModelsService


async def test_seeding():
    print('Testing comprehensive model seeding...')
    
    # Force refresh to test our new seed function
    await seed_models(force_refresh=True)
    
    # Check what we have now
    service = DatabaseCuratedModelsService()
    models = await service.get_models()
    
    print(f'Total models after seeding: {len(models)}')
    
    # Check for specific models
    grok_4 = [m for m in models if m.get('id') == 'grok-4-latest']
    if grok_4:
        model = grok_4[0]
        print('✓ Grok-4-latest found with correct spec:')
        print(f'  Description: {model.get("description", "N/A")}')
        print(f'  Context window: {model.get("context_window", "N/A")}')
        caps = model.get('capabilities', {})
        print(f'  Reasoning: {caps.get("reasoning", "N/A")}')
    else:
        print('✗ Grok-4-latest not found')
    
    # Check for O3 Pro
    o3_pro = [m for m in models if m.get('id') == 'o3-pro']
    if o3_pro:
        model = o3_pro[0]
        print('✓ O3-Pro found:')
        print(f'  Description: {model.get("description", "N/A")}')
        print(f'  Context window: {model.get("context_window", "N/A")}')
    else:
        print('✗ O3-Pro not found')
    
    # Count by provider
    providers = Counter([m.get('provider', 'unknown') for m in models])
    print(f'Models by provider: {dict(providers)}')
    
    # List all model IDs
    print('\nAll model IDs:')
    for model in sorted(models, key=lambda x: (x.get('provider', ''), x.get('id', ''))):
        print(f'  {model.get("provider", "unknown")}: {model.get("id", "unknown")}')

if __name__ == '__main__':
    asyncio.run(test_seeding())
