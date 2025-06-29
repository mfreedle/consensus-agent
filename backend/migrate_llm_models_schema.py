"""
Migrate LLM Models table schema

This migration updates the llm_models table to match the new schema requirements.
"""

import asyncio
import logging

from app.database.connection import engine
from sqlalchemy import text

logger = logging.getLogger(__name__)


async def migrate_llm_models_schema():
    """Update llm_models table schema"""
    
    try:
        async with engine.begin() as conn:
            # Check current schema
            result = await conn.execute(text("PRAGMA table_info(llm_models)"))
            columns = [row[1] for row in result.fetchall()]
            
            logger.info(f"Current columns: {columns}")
            
            # Create new table with correct schema
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS llm_models_new (
                    id INTEGER PRIMARY KEY,
                    model_id VARCHAR(100) NOT NULL,
                    provider VARCHAR(50) NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    description VARCHAR(500),
                    max_tokens INTEGER,
                    supports_streaming BOOLEAN DEFAULT TRUE,
                    supports_function_calling BOOLEAN DEFAULT FALSE,
                    supports_vision BOOLEAN DEFAULT FALSE,
                    context_window INTEGER,
                    input_price_per_1k REAL,
                    output_price_per_1k REAL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_available BOOLEAN DEFAULT TRUE,
                    capabilities JSON,
                    provider_metadata JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME
                )
            """))
            
            # Copy existing data if table exists
            if 'model_name' in columns:
                await conn.execute(text("""
                    INSERT INTO llm_models_new 
                    (id, model_id, provider, display_name, description, max_tokens, 
                     supports_streaming, supports_function_calling, is_active, capabilities, created_at)
                    SELECT 
                        id, 
                        model_name as model_id, 
                        provider, 
                        display_name, 
                        description, 
                        max_tokens,
                        supports_streaming, 
                        supports_function_calling, 
                        is_active, 
                        capabilities, 
                        created_at
                    FROM llm_models
                """))
                
                # Drop old table
                await conn.execute(text("DROP TABLE llm_models"))
                
                logger.info("Copied existing data to new schema")
            
            # Rename new table
            await conn.execute(text("ALTER TABLE llm_models_new RENAME TO llm_models"))
            
            logger.info("Successfully migrated llm_models table schema")
                
    except Exception as e:
        logger.error(f"Error in llm_models migration: {e}")
        raise


async def main():
    """Run the migration"""
    await migrate_llm_models_schema()
    print("✅ LLM Models schema migration completed")


if __name__ == "__main__":
    asyncio.run(main())
