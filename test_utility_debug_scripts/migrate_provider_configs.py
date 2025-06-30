"""
Add provider_configs table

This migration adds the provider_configs table for managing AI provider API keys and configurations.
"""

import asyncio
import logging

from app.database.connection import engine
from app.models.provider_config import ProviderConfig
from sqlalchemy import text

logger = logging.getLogger(__name__)


async def migrate_add_provider_configs():
    """Add provider_configs table if it doesn't exist"""
    
    try:
        async with engine.begin() as conn:
            # Check if table exists
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='provider_configs'")
            )
            table_exists = result.fetchone() is not None
            
            if not table_exists:
                # Create the table
                await conn.run_sync(ProviderConfig.metadata.create_all)
                logger.info("Created provider_configs table")
                
                # Insert default provider configurations
                default_providers = [
                    {
                        'provider': 'openai',
                        'display_name': 'OpenAI',
                        'api_base_url': 'https://api.openai.com/v1',
                        'is_active': True,
                        'max_requests_per_minute': 60,
                        'max_tokens_per_request': 4000,
                        'auto_sync_models': True
                    },
                    {
                        'provider': 'grok',
                        'display_name': 'Grok (xAI)',
                        'api_base_url': 'https://api.x.ai/v1',
                        'is_active': True,
                        'max_requests_per_minute': 60,
                        'max_tokens_per_request': 4000,
                        'auto_sync_models': True
                    },
                    {
                        'provider': 'deepseek',
                        'display_name': 'DeepSeek',
                        'api_base_url': 'https://api.deepseek.com/v1',
                        'is_active': False,
                        'max_requests_per_minute': 60,
                        'max_tokens_per_request': 4000,
                        'auto_sync_models': True
                    },
                    {
                        'provider': 'anthropic',
                        'display_name': 'Anthropic',
                        'api_base_url': 'https://api.anthropic.com/v1',
                        'is_active': False,
                        'max_requests_per_minute': 60,
                        'max_tokens_per_request': 4000,
                        'auto_sync_models': True
                    }
                ]
                
                for provider_data in default_providers:
                    await conn.execute(
                        text("""
                            INSERT INTO provider_configs 
                            (provider, display_name, api_base_url, is_active, 
                             max_requests_per_minute, max_tokens_per_request, auto_sync_models)
                            VALUES 
                            (:provider, :display_name, :api_base_url, :is_active,
                             :max_requests_per_minute, :max_tokens_per_request, :auto_sync_models)
                        """),
                        provider_data
                    )
                
                logger.info("Inserted default provider configurations")
            else:
                logger.info("provider_configs table already exists")
                
    except Exception as e:
        logger.error(f"Error in provider_configs migration: {e}")
        raise


async def main():
    """Run the migration"""
    await migrate_add_provider_configs()
    print("✅ Provider configs migration completed")


if __name__ == "__main__":
    asyncio.run(main())
