from typing import List

from app.auth.dependencies import get_current_active_user
from app.database.connection import get_db
from app.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_available_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of available LLM models"""
    
    # For now, return hardcoded models with enhanced information
    # TODO: Fetch from database and sync with actual API availability
    models = [
        {
            "id": "gpt-4o",
            "provider": "openai",
            "display_name": "GPT-4o",
            "description": "Most capable OpenAI model with multimodal abilities",
            "is_active": True,
            "supports_streaming": True,
            "supports_function_calling": True,
            "capabilities": {
                "reasoning": "high",
                "creativity": "high",
                "code": "high",
                "math": "high"
            }
        },
        {
            "id": "gpt-4o-mini",
            "provider": "openai", 
            "display_name": "GPT-4o Mini",
            "description": "Faster, cost-effective OpenAI model",
            "is_active": True,
            "supports_streaming": True,
            "supports_function_calling": True,
            "capabilities": {
                "reasoning": "medium",
                "creativity": "medium", 
                "code": "medium",
                "math": "medium"
            }
        },
        {
            "id": "grok-2",
            "provider": "grok",
            "display_name": "Grok-2",
            "description": "xAI's most capable model with real-time knowledge",
            "is_active": True,
            "supports_streaming": True,
            "supports_function_calling": False,
            "capabilities": {
                "reasoning": "high",
                "creativity": "high",
                "realtime": "high",
                "humor": "high"
            }
        },
        {
            "id": "grok-2-mini",
            "provider": "grok",
            "display_name": "Grok-2 Mini", 
            "description": "Faster Grok model with real-time insights",
            "is_active": True,
            "supports_streaming": True,
            "supports_function_calling": False,
            "capabilities": {
                "reasoning": "medium",
                "creativity": "medium",
                "realtime": "high",
                "humor": "medium"
            }
        },
        {
            "id": "claude-3-5-sonnet",
            "provider": "claude",
            "display_name": "Claude 3.5 Sonnet",
            "description": "Anthropic's most capable model",
            "is_active": False,
            "supports_streaming": True,
            "supports_function_calling": True,
            "capabilities": {
                "reasoning": "high",
                "creativity": "high",
                "analysis": "high",
                "safety": "high"
            }
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
