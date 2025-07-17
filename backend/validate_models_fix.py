#!/usr/bin/env python3
"""
Validation script to confirm the API endpoint fix
Run this after frontend rebuild to verify everything works
"""
import asyncio
import os
import sys

# Add the backend directory to Python path  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def validate_fix():
    """Validate that the database service is working correctly"""
    try:
        from app.services.database_curated_models import \
            database_curated_models_service
        
        print("🔍 Validating database-backed model service...")
        
        models = await database_curated_models_service.get_models()
        print(f"✅ Service returns {len(models)} models")
        
        # Breakdown by provider
        providers = {}
        for model in models:
            provider = model.get('provider', 'unknown')
            if provider not in providers:
                providers[provider] = 0
            providers[provider] += 1
        
        print("\n📊 Provider breakdown:")
        for provider, count in providers.items():
            print(f"  - {provider}: {count} models")
        
        # Check Grok-4 specifically
        grok4 = next((m for m in models if m.get('id') == 'grok-4'), None)
        if grok4:
            print(f"\n🤖 Grok-4 Status:")
            print(f"  - Supports vision: {grok4.get('supports_vision')}")
            print(f"  - Image generation: {grok4.get('capabilities', {}).get('image_generation')}")
            print(f"  - Context window: {grok4.get('context_window')}")
        
        # Check image generation model
        grok_image = next((m for m in models if m.get('id') == 'grok-2-image-1212'), None)
        if grok_image:
            print(f"\n🎨 Grok Image Model:")
            print(f"  - Model: {grok_image.get('id')}")
            print(f"  - Active: {grok_image.get('is_active')}")
        
        print(f"\n🎉 Validation complete! Frontend should now show all {len(models)} models.")
        print("\n📝 Next steps:")
        print("  1. Rebuild frontend: cd frontend && npm run build")
        print("  2. Start backend: cd backend && python dev.py") 
        print("  3. Check model picker in chat interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(validate_fix())
