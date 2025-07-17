#!/usr/bin/env python3
import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def check_grok_models():
    from app.database.connection import AsyncSessionLocal
    from app.models.llm_model import LLMModel
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(LLMModel).where(LLMModel.provider == 'grok')
        )
        grok_models = result.scalars().all()
        
        print(f'Found {len(grok_models)} Grok models:')
        for model in grok_models:
            status = "Active" if model.is_active else "Inactive"
            print(f'  - {model.model_id} ({status})')
            if 'grok-4' in model.model_id.lower():
                print(f'    *** This is Grok-4! ***')
                print(f'        Supports vision: {model.supports_vision}')
                print(f'        Capabilities: {model.capabilities}')

if __name__ == "__main__":
    asyncio.run(check_grok_models())
