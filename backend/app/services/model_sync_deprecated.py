"""
Model sync service for fetching models from different AI providers
"""
import asyncio
import logging
from typing import Dict, List, Optional

import httpx
from app.config import settings
from app.models.provider_config import ProviderConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ModelSyncService:
    """Service for synchronizing models from AI providers"""
    
    def __init__(self):
        self.timeout = 30  # seconds
        
    async def get_provider_config(self, provider: str, db: AsyncSession = None) -> Optional[Dict]:
        """Get provider configuration from database or environment"""
        if db:
            try:
                stmt = select(ProviderConfig).where(
                    ProviderConfig.provider == provider,
                    ProviderConfig.is_active.is_(True)
                )
                result = await db.execute(stmt)
                config = result.scalar_one_or_none()
                
                if config and config.api_key:
                    return {
                        "api_key": config.api_key,
                        "api_base_url": config.api_base_url,
                        "organization_id": config.organization_id
                    }
            except Exception as e:
                logger.warning(f"Error fetching {provider} config from database: {e}")
        
        # Fallback to environment variables
        env_configs = {
            "openai": {
                "api_key": settings.openai_api_key,
                "organization_id": settings.openai_org_id
            },
            "grok": {
                "api_key": settings.grok_api_key
            },
            "deepseek": {
                "api_key": settings.deepseek_api_key
            },
            "anthropic": {
                "api_key": settings.anthropic_api_key
            }
        }
        
        return env_configs.get(provider, {})
        
    async def fetch_openai_models(self, db: AsyncSession = None) -> List[Dict]:
        """Fetch models from OpenAI API"""
        config = await self.get_provider_config("openai", db)
        api_key = config.get("api_key")
        
        if not api_key:
            logger.warning("OpenAI API key not configured")
            return []
            
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Add organization header if provided
            if config.get("organization_id"):
                headers["OpenAI-Organization"] = config["organization_id"]
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    
                    # Filter for chat models only
                    chat_models = [
                        "gpt-4.1", "gpt-4.1-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"
                    ]
                    
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        if any(chat_model in model_id for chat_model in chat_models):
                            models.append({
                                "model_id": model_id,
                                "provider": "openai",
                                "display_name": self._format_openai_display_name(model_id),
                                "description": f"OpenAI {model_id}",
                                "is_available": True,
                                "supports_streaming": True,
                                "supports_function_calling": True,
                                "supports_vision": "vision" in model_id or "4o" in model_id,
                                "context_window": self._get_openai_context_window(model_id),
                                "provider_metadata": model
                            })
                    
                    logger.info(f"Fetched {len(models)} OpenAI models")
                    return models
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching OpenAI models: {e}")
            return []
    
    async def fetch_grok_models(self, db: AsyncSession = None) -> List[Dict]:
        """Fetch models from Grok/xAI API"""
        config = await self.get_provider_config("grok", db)
        api_key = config.get("api_key")
        
        if not api_key:
            logger.warning("Grok API key not configured")
            return []
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://api.x.ai/v1/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        models.append({
                            "model_id": model_id,
                            "provider": "grok",
                            "display_name": self._format_grok_display_name(model_id),
                            "description": f"xAI {model_id}",
                            "is_available": True,
                            "supports_streaming": True,
                            "supports_function_calling": False,
                            "supports_vision": False,
                            "context_window": 128000,  # Grok models typically have 128k context
                            "provider_metadata": model
                        })
                    
                    logger.info(f"Fetched {len(models)} Grok models")
                    return models
                else:
                    logger.error(f"Grok API error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching Grok models: {e}")
            return []
    
    async def fetch_deepseek_models(self, db: AsyncSession = None) -> List[Dict]:
        """Fetch models from DeepSeek API"""
        config = await self.get_provider_config("deepseek", db)
        api_key = config.get("api_key")
        
        if not api_key:
            logger.warning("DeepSeek API key not configured")
            return []
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://api.deepseek.com/v1/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        models.append({
                            "model_id": model_id,
                            "provider": "deepseek",
                            "display_name": self._format_deepseek_display_name(model_id),
                            "description": f"DeepSeek {model_id}",
                            "is_available": True,
                            "supports_streaming": True,
                            "supports_function_calling": True,
                            "supports_vision": False,
                            "context_window": 64000,  # DeepSeek models typically have 64k context
                            "provider_metadata": model
                        })
                    
                    logger.info(f"Fetched {len(models)} DeepSeek models")
                    return models
                else:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching DeepSeek models: {e}")
            return []
    
    async def fetch_anthropic_models(self, db: AsyncSession = None) -> List[Dict]:
        """Fetch models from Anthropic API"""
        config = await self.get_provider_config("anthropic", db)
        api_key = config.get("api_key")
        
        if not api_key:
            logger.warning("Anthropic API key not configured")
            return []
            
        # Anthropic doesn't have a public models endpoint, so we'll use known models
        # This would need to be updated when new models are released
        known_models = [
            {
                "model_id": "claude-3-5-sonnet-20241022",
                "display_name": "Claude 3.5 Sonnet",
                "description": "Anthropic's most capable model",
                "context_window": 200000,
                "supports_vision": True
            },
            {
                "model_id": "claude-3-sonnet-20240229",
                "display_name": "Claude 3 Sonnet",
                "description": "Balanced model for general tasks",
                "context_window": 200000,
                "supports_vision": True
            },
            {
                "model_id": "claude-3-haiku-20240307",
                "display_name": "Claude 3 Haiku",
                "description": "Fast and efficient model",
                "context_window": 200000,
                "supports_vision": True
            }
        ]
        
        models = []
        for model_info in known_models:
            models.append({
                "model_id": model_info["model_id"],
                "provider": "anthropic",
                "display_name": model_info["display_name"],
                "description": model_info["description"],
                "is_available": True,
                "supports_streaming": True,
                "supports_function_calling": True,
                "supports_vision": model_info.get("supports_vision", False),
                "context_window": model_info.get("context_window", 200000),
                "provider_metadata": model_info
            })
        
        logger.info(f"Added {len(models)} Anthropic models")
        return models
    
    async def sync_all_models(self, db: AsyncSession = None) -> Dict[str, List[Dict]]:
        """Sync models from all providers"""
        logger.info("Starting model sync from all providers")
        
        tasks = [
            self.fetch_openai_models(db),
            self.fetch_grok_models(db),
            self.fetch_deepseek_models(db),
            self.fetch_anthropic_models(db)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        synced_models = {
            "openai": results[0] if not isinstance(results[0], Exception) else [],
            "grok": results[1] if not isinstance(results[1], Exception) else [],
            "deepseek": results[2] if not isinstance(results[2], Exception) else [],
            "anthropic": results[3] if not isinstance(results[3], Exception) else []
        }
        
        total_models = sum(len(models) for models in synced_models.values())
        logger.info(f"Model sync completed. Total models: {total_models}")
        
        return synced_models
    
    def _format_openai_display_name(self, model_id: str) -> str:
        """Format OpenAI model ID to display name"""
        name_map = {
            "gpt-4.1": "gpt-4.1",
            "gpt-4.1-mini": "gpt-4.1 Mini",
            "gpt-4-turbo": "GPT-4 Turbo",
            "gpt-4": "GPT-4",
            "gpt-3.5-turbo": "GPT-3.5 Turbo"
        }
        return name_map.get(model_id, model_id.replace("-", " ").title())
    
    def _format_grok_display_name(self, model_id: str) -> str:
        """Format Grok model ID to display name"""
        return model_id.replace("-", " ").replace("grok", "Grok").title()
    
    def _format_deepseek_display_name(self, model_id: str) -> str:
        """Format DeepSeek model ID to display name"""
        return model_id.replace("-", " ").replace("deepseek", "DeepSeek").title()
    
    def _get_openai_context_window(self, model_id: str) -> int:
        """Get context window for OpenAI models"""
        context_windows = {
            "gpt-4.1": 128000,
            "gpt-4.1-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385
        }
        return context_windows.get(model_id, 8192)


# Global instance
model_sync_service = ModelSyncService()
