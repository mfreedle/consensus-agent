#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def check_image_models():
    from app.database.connection import AsyncSessionLocal
    from app.models.llm_model import LLMModel
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(LLMModel).where(LLMModel.supports_vision == True)
        )
        vision_models = result.scalars().all()
        
        print(f'Found {len(vision_models)} models with vision support:')
        for model in vision_models:
            print(f'  - {model.model_id} ({model.provider})')
            if model.capabilities:
                caps = str(model.capabilities).lower()
                if 'image_generation' in caps or 'generation' in caps:
                    print(f'    -> Has image generation capabilities')
                if 'dall-e' in model.model_id:
                    print(f'    -> DALL-E image generation model')

if __name__ == "__main__":
    asyncio.run(check_image_models())
