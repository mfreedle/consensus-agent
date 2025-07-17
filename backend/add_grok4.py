#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def add_grok4():
    from app.services.database_curated_models import \
        database_curated_models_service
    
    grok4_model = {
        "id": "grok-4",
        "provider": "grok",
        "display_name": "Grok 4",
        "description": "Grok 4 with image generation capabilities",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": False,
        "supports_vision": True,  # Vision support for image generation
        "context_window": 128000,
        "capabilities": {
            "reasoning": "high",
            "creativity": "high",
            "image_generation": True,
            "realtime": "high",
            "humor": "high"
        }
    }
    
    try:
        result = await database_curated_models_service.add_model(grok4_model)
        if result:
            print("✅ Successfully added Grok-4 to the database!")
            
            # Verify it was added
            models = await database_curated_models_service.get_models()
            grok4_found = False
            for model in models:
                if model["id"] == "grok-4":
                    grok4_found = True
                    print(f"✅ Verification: Grok-4 found in database")
                    print(f"   - Display Name: {model['display_name']}")
                    print(f"   - Supports Vision: {model['supports_vision']}")
                    print(f"   - Capabilities: {model['capabilities']}")
                    break
            
            if not grok4_found:
                print("❌ Grok-4 was not found after adding")
        else:
            print("❌ Failed to add Grok-4 (may already exist)")
            
    except Exception as e:
        print(f"❌ Error adding Grok-4: {e}")

if __name__ == "__main__":
    asyncio.run(add_grok4())
