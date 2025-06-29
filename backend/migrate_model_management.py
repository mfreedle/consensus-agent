"""
Database migration script to add new model management tables
Run this after implementing the new model management features
"""
import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import engine
from app.models.llm_model import LLMModel
from app.models.provider_config import ProviderConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def migrate_database():
    """Create new tables and migrate existing data"""
    
    print("🔄 Starting database migration...")
    
    try:
        # Import all models to ensure they're registered
        from app.models import chat, document_approval, files, user

        # Create all tables
        async with engine.begin() as conn:
            # Import Base after all models are loaded
            from app.database.connection import Base
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully")
        
        # Create default provider configurations
        async with AsyncSession(engine) as session:
            await create_default_providers(session)
        
        print("✅ Database migration completed successfully")
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        raise


async def create_default_providers(session: AsyncSession):
    """Create default provider configurations"""
    
    providers = [
        {
            "provider": "openai",
            "display_name": "OpenAI",
            "api_base_url": "https://api.openai.com/v1",
            "is_active": True,
            "max_requests_per_minute": 60,
            "max_tokens_per_request": 4000,
            "auto_sync_models": True
        },
        {
            "provider": "grok",
            "display_name": "Grok (xAI)",
            "api_base_url": "https://api.x.ai/v1",
            "is_active": True,
            "max_requests_per_minute": 60,
            "max_tokens_per_request": 4000,
            "auto_sync_models": True
        },
        {
            "provider": "deepseek",
            "display_name": "DeepSeek",
            "api_base_url": "https://api.deepseek.com/v1",
            "is_active": True,
            "max_requests_per_minute": 60,
            "max_tokens_per_request": 4000,
            "auto_sync_models": True
        },
        {
            "provider": "anthropic",
            "display_name": "Anthropic",
            "api_base_url": "https://api.anthropic.com/v1",
            "is_active": True,
            "max_requests_per_minute": 60,
            "max_tokens_per_request": 4000,
            "auto_sync_models": True
        }
    ]
    
    for provider_data in providers:
        # Check if provider already exists
        stmt = select(ProviderConfig).where(ProviderConfig.provider == provider_data["provider"])
        result = await session.execute(stmt)
        existing_provider = result.scalar_one_or_none()
        
        if not existing_provider:
            provider = ProviderConfig(**provider_data)
            session.add(provider)
            print(f"✅ Created provider: {provider_data['display_name']}")
    
    await session.commit()


async def create_default_models(session: AsyncSession):
    """Create default model entries"""
    
    default_models = [
        {
            "model_id": "gpt-4o",
            "provider": "openai",
            "display_name": "GPT-4o",
            "description": "Most capable OpenAI model with multimodal abilities",
            "is_active": True,
            "is_available": True,
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_vision": True,
            "context_window": 128000,
            "capabilities": {
                "reasoning": "high",
                "creativity": "high",
                "code": "high",
                "math": "high"
            }
        },
        {
            "model_id": "grok-2",
            "provider": "grok",
            "display_name": "Grok-2",
            "description": "xAI's most capable model with real-time knowledge",
            "is_active": True,
            "is_available": True,
            "supports_streaming": True,
            "supports_function_calling": False,
            "supports_vision": False,
            "context_window": 128000,
            "capabilities": {
                "reasoning": "high",
                "creativity": "high",
                "realtime": "high",
                "humor": "high"
            }
        },
        {
            "model_id": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
            "display_name": "Claude 3.5 Sonnet",
            "description": "Anthropic's most capable model",
            "is_active": False,
            "is_available": True,
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_vision": True,
            "context_window": 200000,
            "capabilities": {
                "reasoning": "high",
                "creativity": "high",
                "analysis": "high",
                "safety": "high"
            }
        }
    ]
    
    for model_data in default_models:
        # Check if model already exists
        stmt = select(LLMModel).where(
            LLMModel.model_id == model_data["model_id"],
            LLMModel.provider == model_data["provider"]
        )
        result = await session.execute(stmt)
        existing_model = result.scalar_one_or_none()
        
        if not existing_model:
            model = LLMModel(**model_data)
            session.add(model)
            print(f"✅ Created model: {model_data['display_name']}")
    
    await session.commit()


if __name__ == "__main__":
    print("🚀 Running database migration for model management...")
    asyncio.run(migrate_database())
    print("🎉 Migration completed!")
