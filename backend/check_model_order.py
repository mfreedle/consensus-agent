#!/usr/bin/env python3
import asyncio

from app.services.database_curated_models import \
    database_curated_models_service


async def check_order():
    models = await database_curated_models_service.get_models()
    print("First 5 models in order:")
    for i, model in enumerate(models[:5]):
        active = model.get("is_active")
        print(f"{i+1}. {model['id']} - {model['display_name']} - Active: {active}")
    
    print("\nLooking for gpt-4.1:")
    for i, model in enumerate(models):
        if "gpt-4.1" in model["id"]:
            print(f"Position {i+1}: {model['id']} - {model['display_name']}")

asyncio.run(check_order())
