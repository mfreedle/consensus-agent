#!/usr/bin/env python3
"""
Debug the exact model structure returned by the API
"""

import asyncio
import json

from app.services.database_curated_models import \
    database_curated_models_service


async def debug_model_structure():
    models = await database_curated_models_service.get_models()
    
    print(f"Total models: {len(models)}")
    print("\nFirst model structure:")
    if models:
        first_model = models[0]
        print(json.dumps(first_model, indent=2, default=str))
    
    print(f"\nActive models check:")
    active_models = [m for m in models if m.get('is_active') != False]
    print(f"Models where is_active != False: {len(active_models)}")
    
    active_models_true = [m for m in models if m.get('is_active') == True]
    print(f"Models where is_active == True: {len(active_models_true)}")
    
    print(f"\nFirst 5 models is_active values:")
    for i, model in enumerate(models[:5]):
        print(f"  {i+1}. {model['id']}: is_active = {model.get('is_active')} (type: {type(model.get('is_active'))})")

if __name__ == "__main__":
    asyncio.run(debug_model_structure())
