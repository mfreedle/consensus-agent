#!/usr/bin/env python3
"""
Validation script to verify all models from LLM_models_to_use.md are in the database
"""

import asyncio

from app.services.database_curated_models import DatabaseCuratedModelsService


async def validate_models_from_list():
    """Validate that all models from LLM_models_to_use.md are in the database"""
    
    # Expected models from LLM_models_to_use.md
    expected_models = [
        "grok-4-latest",
        "grok-3-latest", 
        "grok-3-mini-latest",
        "grok-3-fast-latest",
        "grok-3-mini-fast-latest",
        "grok-2-image-latest",
        "gpt-4.1",
        "gpt-4.1-mini",
        "dall-e-3",
        "o4-mini",
        "o3",
        "o3-pro",
        "o3-mini",
        "o1",
        "o1-pro",
        "gpt-4.1-nano",
        "o3-deep-research",
        "o4-mini-deep-research",
        "deepseek-chat",
        "deepseek-reasoner",
        "claude-opus-4-0",
        "claude-sonnet-4-0",
        "claude-3-7-sonnet-latest"
    ]
    
    print(f"📋 Validating {len(expected_models)} models from LLM_models_to_use.md")
    
    # Get models from database
    service = DatabaseCuratedModelsService()
    db_models = await service.get_models()
    db_model_ids = {model.get('id') for model in db_models}
    
    print(f"🔍 Found {len(db_models)} models in database")
    
    # Check each expected model
    missing_models = []
    found_models = []
    
    for expected_model in expected_models:
        if expected_model in db_model_ids:
            found_models.append(expected_model)
            print(f"✅ {expected_model}")
        else:
            missing_models.append(expected_model)
            print(f"❌ {expected_model} - MISSING")
    
    print("\n📊 Summary:")
    print(f"✅ Found: {len(found_models)}/{len(expected_models)} models")
    print(f"❌ Missing: {len(missing_models)} models")
    
    if missing_models:
        print("\n⚠️  Missing models:")
        for model in missing_models:
            print(f"   - {model}")
    else:
        print("\n🎉 All models from LLM_models_to_use.md are present in the database!")
    
    # Show any extra models not in the list
    extra_models = db_model_ids - set(expected_models)
    if extra_models:
        print("\n📝 Extra models in database (not in LLM_models_to_use.md):")
        for model in sorted([m for m in extra_models if m is not None]):
            print(f"   + {model}")

if __name__ == "__main__":
    asyncio.run(validate_models_from_list())
