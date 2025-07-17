"""
Database-backed curated models service for managing approved models
"""
import logging
from typing import Dict, List

from app.database.connection import AsyncSessionLocal
from app.models.llm_model import LLMModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Default models to seed the database with
DEFAULT_CURATED_MODELS = [
    # Grok models
    {
        "model_id": "grok-3-latest",
        "provider": "grok",
        "display_name": "Grok 3 Latest",
        "description": "Latest Grok 3 model with enhanced reasoning",
        "is_active": True,
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
        "model_id": "grok-3-fast-latest",
        "provider": "grok",
        "display_name": "Grok 3 Fast Latest",
        "description": "Faster version of Grok 3 with optimized performance",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": False,
        "supports_vision": False,
        "context_window": 128000,
        "capabilities": {
            "reasoning": "high",
            "creativity": "medium",
            "realtime": "high",
            "speed": "high"
        }
    },
    {
        "model_id": "grok-2-image",
        "provider": "grok",
        "display_name": "Grok 2 Image Generator",
        "description": "xAI's dedicated image generation model",
        "is_active": True,
        "supports_streaming": False,
        "supports_function_calling": False,
        "supports_vision": False,
        "context_window": 4000,
        "capabilities": {
            "image_generation": "high",
            "creativity": "high",
            "art": "high"
        }
    },
    # OpenAI models
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
            "coding": "high",
            "vision": "high",
            "function_calling": "high"
        }
    },
    # Claude models
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
    },
    # DeepSeek models
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
    }
]


class DatabaseCuratedModelsService:
    """Database-backed service for managing curated models"""
    
    async def get_models(self) -> List[Dict]:
        """Get all active curated models from database"""
        try:
            async with AsyncSessionLocal() as db:
                # Query active models
                result = await db.execute(
                    select(LLMModel).where(LLMModel.is_active.is_(True))
                )
                models = result.scalars().all()
                
                # Convert to dict format compatible with existing API
                model_list = []
                for model in models:
                    model_dict = {
                        "id": model.model_id,
                        "provider": model.provider,
                        "display_name": model.display_name,
                        "description": model.description,
                        "is_active": model.is_active,
                        "supports_streaming": model.supports_streaming,
                        "supports_function_calling": model.supports_function_calling,
                        "supports_vision": model.supports_vision,
                        "context_window": model.context_window,
                        "capabilities": model.capabilities or {}
                    }
                    model_list.append(model_dict)
                
                # If no models found, seed with defaults
                if not model_list:
                    logger.info("No models found in database, seeding with defaults...")
                    await self._seed_default_models(db)
                    return await self.get_models()  # Recursive call after seeding
                
                return model_list
                
        except Exception as e:
            logger.error(f"Error fetching models from database: {e}")
            # Fallback to defaults if database fails
            return self._convert_defaults_to_dict_format()
    
    async def add_model(self, model_data: Dict) -> bool:
        """Add a new model to the database"""
        try:
            async with AsyncSessionLocal() as db:
                # Check if model already exists
                existing = await db.execute(
                    select(LLMModel).where(LLMModel.model_id == model_data["id"])
                )
                if existing.scalar_one_or_none():
                    return False  # Model already exists
                
                # Create new model
                new_model = LLMModel(
                    model_id=model_data["id"],
                    provider=model_data["provider"],
                    display_name=model_data["display_name"],
                    description=model_data.get("description"),
                    is_active=model_data.get("is_active", True),
                    supports_streaming=model_data.get("supports_streaming", True),
                    supports_function_calling=model_data.get("supports_function_calling", False),
                    supports_vision=model_data.get("supports_vision", False),
                    context_window=model_data.get("context_window"),
                    capabilities=model_data.get("capabilities", {})
                )
                
                db.add(new_model)
                await db.commit()
                logger.info(f"Added model {model_data['id']} to database")
                return True
                
        except Exception as e:
            logger.error(f"Error adding model to database: {e}")
            return False
    
    async def update_model(self, model_id: str, model_data: Dict) -> bool:
        """Update an existing model in the database"""
        try:
            async with AsyncSessionLocal() as db:
                # Find existing model
                result = await db.execute(
                    select(LLMModel).where(LLMModel.model_id == model_id)
                )
                existing_model = result.scalar_one_or_none()
                
                if not existing_model:
                    return False  # Model not found
                
                # Update fields
                existing_model.provider = model_data.get("provider", existing_model.provider)
                existing_model.display_name = model_data.get("display_name", existing_model.display_name)
                existing_model.description = model_data.get("description", existing_model.description)
                existing_model.is_active = model_data.get("is_active", existing_model.is_active)
                existing_model.supports_streaming = model_data.get("supports_streaming", existing_model.supports_streaming)
                existing_model.supports_function_calling = model_data.get("supports_function_calling", existing_model.supports_function_calling)
                existing_model.supports_vision = model_data.get("supports_vision", existing_model.supports_vision)
                existing_model.context_window = model_data.get("context_window", existing_model.context_window)
                existing_model.capabilities = model_data.get("capabilities", existing_model.capabilities)
                
                await db.commit()
                logger.info(f"Updated model {model_id} in database")
                return True
                
        except Exception as e:
            logger.error(f"Error updating model in database: {e}")
            return False
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete a model from the database"""
        try:
            async with AsyncSessionLocal() as db:
                # Find and delete model
                result = await db.execute(
                    select(LLMModel).where(LLMModel.model_id == model_id)
                )
                existing_model = result.scalar_one_or_none()
                
                if not existing_model:
                    return False  # Model not found
                
                await db.delete(existing_model)
                await db.commit()
                logger.info(f"Deleted model {model_id} from database")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting model from database: {e}")
            return False
    
    async def toggle_model(self, model_id: str, is_active: bool) -> bool:
        """Toggle a model's active status"""
        try:
            async with AsyncSessionLocal() as db:
                # Find model
                result = await db.execute(
                    select(LLMModel).where(LLMModel.model_id == model_id)
                )
                existing_model = result.scalar_one_or_none()
                
                if not existing_model:
                    return False  # Model not found
                
                existing_model.is_active = is_active
                await db.commit()
                logger.info(f"Toggled model {model_id} to active={is_active}")
                return True
                
        except Exception as e:
            logger.error(f"Error toggling model status: {e}")
            return False
    
    async def _seed_default_models(self, db: AsyncSession):
        """Seed database with default models"""
        for model_data in DEFAULT_CURATED_MODELS:
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
        
        await db.commit()
        logger.info(f"Seeded database with {len(DEFAULT_CURATED_MODELS)} default models")
    
    def _convert_defaults_to_dict_format(self) -> List[Dict]:
        """Convert default models to dict format for fallback"""
        result = []
        for model in DEFAULT_CURATED_MODELS:
            model_dict = {
                "id": model["model_id"],
                "provider": model["provider"],
                "display_name": model["display_name"],
                "description": model["description"],
                "is_active": model["is_active"],
                "supports_streaming": model["supports_streaming"],
                "supports_function_calling": model["supports_function_calling"],
                "supports_vision": model["supports_vision"],
                "context_window": model["context_window"],
                "capabilities": model["capabilities"]
            }
            result.append(model_dict)
        return result


# Global instance
database_curated_models_service = DatabaseCuratedModelsService()
