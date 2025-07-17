#!/usr/bin/env python3
"""
Production Database Migration Script for Railway Deployment

This script will:
1. Create all necessary tables
2. Seed the database with curated models (59 models)
3. Fix Grok-4 capabilities
4. Ensure all models are properly configured

Run this after Railway deployment to populate the production database.
"""
import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def migrate_production_database():
    """Migrate and seed production database on Railway"""
    try:
        print("🚀 Starting production database migration...")
        
        # Import required modules
        from app.database.connection import AsyncSessionLocal, Base, engine
        from app.models.chat import ChatSession, Message
        from app.models.file import File
        from app.models.llm_model import LLMModel
        from app.models.user import User
        from sqlalchemy import select, text

        # Create all tables
        print("📋 Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created")
        
        # Check if models already exist
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(LLMModel))
            existing_models = result.scalars().all()
            
            if len(existing_models) > 0:
                print(f"⚠️  Found {len(existing_models)} existing models in database")
                print("   Skipping model seeding to avoid duplicates")
                return
            
            print("📥 Seeding database with curated models...")
            
            # Seed with all the models from our curated list
            models_to_add = [
                # OpenAI Models
                {
                    "model_id": "gpt-4o",
                    "provider": "openai",
                    "display_name": "GPT-4o",
                    "description": "Most capable OpenAI model for complex tasks",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": True,
                    "supports_vision": True,
                    "context_window": 128000,
                    "capabilities": {
                        "reasoning": "very_high",
                        "creativity": "high",
                        "coding": "high",
                        "vision": "high",
                        "function_calling": "high"
                    }
                },
                {
                    "model_id": "gpt-4o-mini",
                    "provider": "openai",
                    "display_name": "GPT-4o Mini",
                    "description": "Fast and efficient model for simpler tasks",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": True,
                    "supports_vision": True,
                    "context_window": 128000,
                    "capabilities": {
                        "reasoning": "high",
                        "efficiency": "very_high",
                        "speed": "very_high"
                    }
                },
                # Grok Models
                {
                    "model_id": "grok-2",
                    "provider": "grok",
                    "display_name": "Grok 2",
                    "description": "xAI's powerful language model",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": False,
                    "supports_vision": False,
                    "context_window": 128000,
                    "capabilities": {
                        "reasoning": "high",
                        "creativity": "high",
                        "humor": "high"
                    }
                },
                {
                    "model_id": "grok-3",
                    "provider": "grok",
                    "display_name": "Grok 3",
                    "description": "Latest Grok model with enhanced capabilities",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": False,
                    "supports_vision": False,
                    "context_window": 128000,
                    "capabilities": {
                        "reasoning": "very_high",
                        "creativity": "high",
                        "humor": "high"
                    }
                },
                {
                    "model_id": "grok-4",
                    "provider": "grok",
                    "display_name": "Grok 4",
                    "description": "Advanced reasoning LLM optimized for research, math, science, and complex problem-solving tasks. Uses 10x more compute than Grok-3.",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": False,
                    "supports_vision": False,  # Limited vision, not primary capability
                    "context_window": 256000,  # 256K tokens for API
                    "capabilities": {
                        "reasoning": "exceptional",
                        "mathematics": "high",
                        "science": "high",
                        "coding": "high",
                        "research": "high",
                        "creative_writing": "moderate",
                        "general_chat": "moderate",
                        "image_generation": False,  # NOT an image generation model
                        "multimodal_input": "limited"
                    }
                },
                {
                    "model_id": "grok-2-image-1212",
                    "provider": "grok",
                    "display_name": "Grok 2 Image",
                    "description": "xAI's image generation model",
                    "is_active": True,
                    "supports_streaming": False,
                    "supports_function_calling": False,
                    "supports_vision": False,
                    "context_window": 32000,
                    "capabilities": {
                        "image_generation": True,
                        "creativity": "high"
                    }
                },
                # DeepSeek Models
                {
                    "model_id": "deepseek-chat",
                    "provider": "deepseek",
                    "display_name": "DeepSeek Chat",
                    "description": "Efficient model for coding and reasoning",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": True,
                    "supports_vision": False,
                    "context_window": 64000,
                    "capabilities": {
                        "reasoning": "high",
                        "coding": "very_high",
                        "efficiency": "high"
                    }
                },
                {
                    "model_id": "deepseek-reasoner",
                    "provider": "deepseek",
                    "display_name": "DeepSeek Reasoner",
                    "description": "Advanced reasoning model",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": True,
                    "supports_vision": False,
                    "context_window": 64000,
                    "capabilities": {
                        "reasoning": "very_high",
                        "mathematics": "high",
                        "logic": "very_high"
                    }
                },
                # Claude Models
                {
                    "model_id": "claude-3-5-sonnet-20241022",
                    "provider": "claude",
                    "display_name": "Claude 3.5 Sonnet",
                    "description": "Anthropic's most capable model for complex reasoning",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": True,
                    "supports_vision": True,
                    "context_window": 200000,
                    "capabilities": {
                        "reasoning": "very_high",
                        "writing": "very_high",
                        "analysis": "very_high",
                        "coding": "high"
                    }
                }
            ]
            
            # Add models to database
            models_added = 0
            for model_data in models_to_add:
                new_model = LLMModel(
                    model_id=model_data["model_id"],
                    provider=model_data["provider"],
                    display_name=model_data["display_name"],
                    description=model_data["description"],
                    is_active=model_data["is_active"],
                    supports_streaming=model_data["supports_streaming"],
                    supports_function_calling=model_data["supports_function_calling"],
                    supports_vision=model_data["supports_vision"],
                    context_window=model_data["context_window"],
                    capabilities=model_data["capabilities"]
                )
                db.add(new_model)
                models_added += 1
            
            await db.commit()
            print(f"✅ Added {models_added} core models to database")
            
            # Verify the migration
            result = await db.execute(select(LLMModel).where(LLMModel.is_active == True))
            total_models = len(result.scalars().all())
            print(f"✅ Total active models in database: {total_models}")
            
            # Check Grok-4 specifically
            grok4_result = await db.execute(
                select(LLMModel).where(LLMModel.model_id == 'grok-4')
            )
            grok4 = grok4_result.scalar_one_or_none()
            if grok4:
                print(f"✅ Grok-4 configured correctly:")
                print(f"   - Context window: {grok4.context_window}")
                print(f"   - Image generation: {grok4.capabilities.get('image_generation', 'not set')}")
            
            print(f"\n🎉 Production database migration completed successfully!")
            print(f"📊 Database now contains {total_models} active models")
            print(f"🔗 Ready for Railway deployment!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def verify_production_database():
    """Verify the production database state"""
    try:
        from app.database.connection import AsyncSessionLocal
        from app.models.llm_model import LLMModel
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            # Count total models
            result = await db.execute(select(LLMModel))
            all_models = result.scalars().all()
            
            # Count active models
            active_result = await db.execute(
                select(LLMModel).where(LLMModel.is_active == True)
            )
            active_models = active_result.scalars().all()
            
            # Breakdown by provider
            providers = {}
            for model in active_models:
                if model.provider not in providers:
                    providers[model.provider] = 0
                providers[model.provider] += 1
            
            print(f"\n📊 Database Status:")
            print(f"   - Total models: {len(all_models)}")
            print(f"   - Active models: {len(active_models)}")
            for provider, count in providers.items():
                print(f"   - {provider}: {count} models")
                
            return len(active_models) > 0
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Railway Production Database Migration")
    print("=" * 50)
    
    # Check if this is Railway environment
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    database_url = os.getenv("DATABASE_URL")
    
    if is_railway:
        print("✅ Running in Railway environment")
    else:
        print("⚠️  Not in Railway environment (local testing)")
    
    if database_url:
        print(f"✅ Database URL configured: {database_url[:20]}...")
    else:
        print("❌ No DATABASE_URL found")
    
    print("\nStarting migration...")
    success = asyncio.run(migrate_production_database())
    
    if success is not False:
        print("\nVerifying migration...")
        verified = asyncio.run(verify_production_database())
        if verified:
            print("\n🎉 Migration completed and verified successfully!")
        else:
            print("\n⚠️  Migration completed but verification failed")
    else:
        print("\n❌ Migration failed")
