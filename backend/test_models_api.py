#!/usr/bin/env python3
"""
Quick test to check what models the API returns
"""

import asyncio

from app.services.database_curated_models import \
    database_curated_models_service


async def test_api():
    models = await database_curated_models_service.get_models()
    print(f'Total models: {len(models)}')
    for model in models:
        print(f'- {model["id"]} ({model["provider"]}) - {model["display_name"]} - Active: {model["is_active"]}')

if __name__ == "__main__":
    asyncio.run(test_api())
