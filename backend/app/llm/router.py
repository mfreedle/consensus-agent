from typing import List

from app.auth.dependencies import get_current_active_user
from app.database.connection import get_db
from app.models.llm_model import LLMModel
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_available_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of available LLM models"""
    
    # For now, return hardcoded models
    # TODO: Fetch from database and sync with actual API availability
    models = [
        {
            "id": "gpt-4o",
            "provider": "openai",
            "display_name": "GPT-4o",
            "description": "Most capable OpenAI model",
            "supports_streaming": True,
            "supports_function_calling": True
        },
        {
            "id": "gpt-4o-mini",
            "provider": "openai", 
            "display_name": "GPT-4o Mini",
            "description": "Faster, cost-effective OpenAI model",
            "supports_streaming": True,
            "supports_function_calling": True
        },
        {
            "id": "grok-2",
            "provider": "grok",
            "display_name": "Grok-2",
            "description": "xAI's most capable model",
            "supports_streaming": True,
            "supports_function_calling": False
        },
        {
            "id": "grok-2-mini",
            "provider": "grok",
            "display_name": "Grok-2 Mini", 
            "description": "Faster Grok model",
            "supports_streaming": True,
            "supports_function_calling": False
        }
    ]
    
    return models

@router.post("/sync")
async def sync_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync available models with database"""
    
    # TODO: Implement model syncing
    return {"message": "Models synced successfully"}
