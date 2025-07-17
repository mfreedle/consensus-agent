#!/usr/bin/env python3
import asyncio

from app.services.database_curated_models import \
    database_curated_models_service


async def test():
    models = await database_curated_models_service.get_models()
    print(f'Total models: {len(models)}')
    print('First few models:')
    for i, model in enumerate(models[:5]):
        print(f'  {i+1}. ID: {model["id"]}, Name: {model["display_name"]}, Provider: {model["provider"]}')
    print()
    print('OpenAI models:')
    openai_models = [m for m in models if m['provider'] == 'openai']
    for model in openai_models[:3]:
        print(f'  - {model["id"]} -> {model["display_name"]}')

asyncio.run(test())
