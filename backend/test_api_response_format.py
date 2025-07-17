#!/usr/bin/env python3
import asyncio

from app.services.database_curated_models import \
    database_curated_models_service


async def test_api_response_format():
    result = await database_curated_models_service.get_models()
    print(f"Type: {type(result)}")
    print(f"Is list: {isinstance(result, list)}")
    if hasattr(result, 'keys'):
        print(f"Keys: {list(result.keys())}")
    print(f"Length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
    
    if isinstance(result, list) and len(result) > 0:
        print(f"First item type: {type(result[0])}")
        print(f"First item: {result[0]}")

asyncio.run(test_api_response_format())
