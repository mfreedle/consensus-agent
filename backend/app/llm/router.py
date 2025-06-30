from typing import List, Optional

from app.auth.dependencies import get_current_active_user
from app.database.connection import get_db
from app.models.llm_model import LLMModel
from app.models.provider_config import ProviderConfig
from app.models.user import User
from app.services.model_sync import model_sync_service
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class ProviderConfigRequest(BaseModel):
    provider: str
    display_name: str
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    organization_id: Optional[str] = None
    is_active: bool = True
    max_requests_per_minute: int = 60
    max_tokens_per_request: int = 4000
    auto_sync_models: bool = True


class ModelToggleRequest(BaseModel):
    model_id: str
    is_active: bool


class ProviderConfigResponse(BaseModel):
    id: int
    provider: str
    display_name: str
    api_base_url: Optional[str]
    organization_id: Optional[str]
    is_active: bool
    max_requests_per_minute: int
    max_tokens_per_request: int
    auto_sync_models: bool
    last_sync_at: Optional[str]
    sync_error: Optional[str]
    has_api_key: bool  # Don't expose the actual key


class ModelSyncResponse(BaseModel):
    success: bool
    message: str
    synced_providers: List[str]
    total_models: int
    errors: Optional[List[str]] = None


@router.get("", response_model=List[dict])
async def get_available_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of available LLM models"""
    
    try:
        # Get models from database
        stmt = select(LLMModel).where(LLMModel.is_available)
        result = await db.execute(stmt)
        db_models = result.scalars().all()
        
        models = []
        for model in db_models:
            models.append({
                "id": model.model_id,
                "provider": model.provider,
                "display_name": model.display_name,
                "description": model.description,
                "is_active": model.is_active,
                "supports_streaming": model.supports_streaming,
                "supports_function_calling": model.supports_function_calling,
                "supports_vision": model.supports_vision,
                "context_window": model.context_window,
                "capabilities": model.capabilities,
                "input_price_per_1k": model.input_price_per_1k,
                "output_price_per_1k": model.output_price_per_1k
            })
        
        # If no models in database, return hardcoded fallback
        if not models:
            models = [
                {
                    "id": "gpt-4o",
                    "provider": "openai",
                    "display_name": "GPT-4o",
                    "description": "Most capable OpenAI model with multimodal abilities",
                    "is_active": True,
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
                    "id": "grok-2",
                    "provider": "grok",
                    "display_name": "Grok-2",
                    "description": "xAI's most capable model with real-time knowledge",
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
                }
            ]
        
        return models
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching models: {str(e)}"
        )


@router.post("/sync", response_model=ModelSyncResponse)
async def sync_models(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync available models from all providers"""
    
    try:
        # Fetch models from all providers
        synced_models = await model_sync_service.sync_all_models(db)
        
        # Update database with new models
        updated_count = 0
        created_count = 0
        errors = []
        
        for provider, models in synced_models.items():
            if isinstance(models, Exception):
                errors.append(f"{provider}: {str(models)}")
                continue
                
            for model_data in models:
                try:
                    # Check if model already exists
                    stmt = select(LLMModel).where(
                        LLMModel.model_id == model_data["model_id"],
                        LLMModel.provider == provider
                    )
                    result = await db.execute(stmt)
                    existing_model = result.scalar_one_or_none()
                    
                    if existing_model:
                        # Update existing model
                        existing_model.display_name = model_data["display_name"]
                        existing_model.description = model_data["description"]
                        existing_model.is_available = model_data["is_available"]
                        existing_model.supports_streaming = model_data["supports_streaming"]
                        existing_model.supports_function_calling = model_data["supports_function_calling"]
                        existing_model.supports_vision = model_data["supports_vision"]
                        existing_model.context_window = model_data["context_window"]
                        existing_model.provider_metadata = model_data["provider_metadata"]
                        updated_count += 1
                    else:
                        # Create new model
                        new_model = LLMModel(
                            model_id=model_data["model_id"],
                            provider=provider,
                            display_name=model_data["display_name"],
                            description=model_data["description"],
                            is_available=model_data["is_available"],
                            supports_streaming=model_data["supports_streaming"],
                            supports_function_calling=model_data["supports_function_calling"],
                            supports_vision=model_data["supports_vision"],
                            context_window=model_data["context_window"],
                            provider_metadata=model_data["provider_metadata"]
                        )
                        db.add(new_model)
                        created_count += 1
                        
                except Exception as model_error:
                    errors.append(f"Error processing {model_data.get('model_id', 'unknown')}: {str(model_error)}")
        
        await db.commit()
        
        total_models = created_count + updated_count
        success_providers = [p for p in synced_models.keys() if not isinstance(synced_models[p], Exception)]
        
        return ModelSyncResponse(
            success=True,
            message=f"Synced {total_models} models from {len(success_providers)} providers",
            synced_providers=success_providers,
            total_models=total_models,
            errors=errors if errors else None
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing models: {str(e)}"
        )


@router.get("/providers", response_model=List[ProviderConfigResponse])
async def get_provider_configs(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get provider configurations (without API keys)"""
    try:
        stmt = select(ProviderConfig)
        result = await db.execute(stmt)
        configs = result.scalars().all()
        
        provider_responses = []
        for config in configs:
            provider_responses.append(ProviderConfigResponse(
                id=config.id,
                provider=config.provider,
                display_name=config.display_name,
                api_base_url=config.api_base_url,
                organization_id=config.organization_id,
                is_active=config.is_active,
                max_requests_per_minute=config.max_requests_per_minute,
                max_tokens_per_request=config.max_tokens_per_request,
                auto_sync_models=config.auto_sync_models,
                last_sync_at=config.last_sync_at.isoformat() if config.last_sync_at else None,
                sync_error=config.sync_error,
                has_api_key=config.api_key is not None and len(config.api_key) > 0
            ))
            
        return provider_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching provider configs: {str(e)}"
        )


@router.post("/providers", response_model=ProviderConfigResponse)
async def create_or_update_provider_config(
    config: ProviderConfigRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update provider configuration"""
    try:
        # Check if provider config already exists
        stmt = select(ProviderConfig).where(ProviderConfig.provider == config.provider)
        result = await db.execute(stmt)
        existing_config = result.scalar_one_or_none()
        
        if existing_config:
            # Update existing config
            existing_config.display_name = config.display_name
            if config.api_key:  # Only update API key if provided
                existing_config.api_key = config.api_key
            existing_config.api_base_url = config.api_base_url
            existing_config.organization_id = config.organization_id
            existing_config.is_active = config.is_active
            existing_config.max_requests_per_minute = config.max_requests_per_minute
            existing_config.max_tokens_per_request = config.max_tokens_per_request
            existing_config.auto_sync_models = config.auto_sync_models
            
            provider_config = existing_config
        else:
            # Create new config
            provider_config = ProviderConfig(
                provider=config.provider,
                display_name=config.display_name,
                api_key=config.api_key,
                api_base_url=config.api_base_url,
                organization_id=config.organization_id,
                is_active=config.is_active,
                max_requests_per_minute=config.max_requests_per_minute,
                max_tokens_per_request=config.max_tokens_per_request,
                auto_sync_models=config.auto_sync_models
            )
            db.add(provider_config)
        
        await db.commit()
        await db.refresh(provider_config)
        
        # If auto_sync_models is enabled and config is active, trigger sync
        if config.auto_sync_models and config.is_active:
            try:
                await model_sync_service.sync_all_models(db)
            except Exception as sync_error:
                # Don't fail the config update if sync fails
                provider_config.sync_error = str(sync_error)
                await db.commit()
        
        return ProviderConfigResponse(
            id=provider_config.id,
            provider=provider_config.provider,
            display_name=provider_config.display_name,
            api_base_url=provider_config.api_base_url,
            organization_id=provider_config.organization_id,
            is_active=provider_config.is_active,
            max_requests_per_minute=provider_config.max_requests_per_minute,
            max_tokens_per_request=provider_config.max_tokens_per_request,
            auto_sync_models=provider_config.auto_sync_models,
            last_sync_at=provider_config.last_sync_at.isoformat() if provider_config.last_sync_at else None,
            sync_error=provider_config.sync_error,
            has_api_key=provider_config.api_key is not None and len(provider_config.api_key) > 0
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating provider config: {str(e)}"
        )


@router.delete("/providers/{provider_id}")
async def delete_provider_config(
    provider_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete provider configuration"""
    try:
        stmt = select(ProviderConfig).where(ProviderConfig.id == provider_id)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider configuration not found"
            )
        
        await db.delete(config)
        await db.commit()
        
        return {"message": f"Provider configuration for {config.display_name} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting provider config: {str(e)}"
        )


@router.post("/sync/{provider}")
async def sync_provider_models(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync models from a specific provider"""
    try:
        # Validate provider
        valid_providers = ["openai", "grok", "deepseek", "anthropic"]
        if provider not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
            )
        
        # Get provider config
        stmt = select(ProviderConfig).where(ProviderConfig.provider == provider)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config or not config.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider {provider} is not configured or inactive"
            )
        
        # Sync models for specific provider
        if provider == "openai":
            models = await model_sync_service.fetch_openai_models(db)
        elif provider == "grok":
            models = await model_sync_service.fetch_grok_models(db)
        elif provider == "deepseek":
            models = await model_sync_service.fetch_deepseek_models(db)
        elif provider == "anthropic":
            models = await model_sync_service.fetch_anthropic_models(db)
        
        # Update database
        created_count = 0
        updated_count = 0
        
        for model_data in models:
            stmt = select(LLMModel).where(
                LLMModel.model_id == model_data["model_id"],
                LLMModel.provider == provider
            )
            result = await db.execute(stmt)
            existing_model = result.scalar_one_or_none()
            
            if existing_model:
                # Update existing model
                existing_model.display_name = model_data["display_name"]
                existing_model.description = model_data["description"]
                existing_model.is_available = model_data["is_available"]
                existing_model.supports_streaming = model_data["supports_streaming"]
                existing_model.supports_function_calling = model_data["supports_function_calling"]
                existing_model.supports_vision = model_data["supports_vision"]
                existing_model.context_window = model_data["context_window"]
                existing_model.provider_metadata = model_data["provider_metadata"]
                updated_count += 1
            else:
                # Create new model
                new_model = LLMModel(
                    model_id=model_data["model_id"],
                    provider=provider,
                    display_name=model_data["display_name"],
                    description=model_data["description"],
                    is_available=model_data["is_available"],
                    supports_streaming=model_data["supports_streaming"],
                    supports_function_calling=model_data["supports_function_calling"],
                    supports_vision=model_data["supports_vision"],
                    context_window=model_data["context_window"],
                    provider_metadata=model_data["provider_metadata"]
                )
                db.add(new_model)
                created_count += 1
        
        await db.commit()
        
        # Update sync timestamp
        config.last_sync_at = func.now()
        config.sync_error = None
        await db.commit()
        
        return {
            "message": f"Successfully synced {len(models)} models from {provider}",
            "provider": provider,
            "created": created_count,
            "updated": updated_count,
            "total": len(models)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing {provider} models: {str(e)}"
        )


@router.post("/toggle")
async def toggle_model(
    toggle_request: ModelToggleRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle model active status"""
    
    try:
        stmt = select(LLMModel).where(LLMModel.model_id == toggle_request.model_id)
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model '{toggle_request.model_id}' not found"
            )
        
        model.is_active = toggle_request.is_active
        await db.commit()
        
        return {
            "message": f"Model '{toggle_request.model_id}' {'activated' if toggle_request.is_active else 'deactivated'}",
            "model_id": toggle_request.model_id,
            "is_active": toggle_request.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling model: {str(e)}"
        )
