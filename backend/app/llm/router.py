import logging
from typing import List, Optional

from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.services.curated_models import curated_models_service
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


class ModelRequest(BaseModel):
    model_id: str
    provider: str
    display_name: str
    description: str
    is_active: bool = True
    supports_streaming: bool = True
    supports_function_calling: bool = False
    supports_vision: bool = False
    context_window: int = 128000
    capabilities: Optional[dict] = None


class ModelToggleRequest(BaseModel):
    model_id: str
    is_active: bool


@router.get("", response_model=List[dict])
async def get_available_models(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of curated LLM models"""
    
    try:
        models = curated_models_service.get_models()
        return models
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching models: {str(e)}"
        )


# Admin endpoints for managing curated models
@router.post("/admin/models", response_model=dict)
async def add_curated_model(
    model_request: ModelRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Add a new model to the curated list (Admin only)"""
    
    # TODO: Add admin role check when roles are implemented
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        model_data = model_request.dict()
        # Map model_id to id for the service
        model_data["id"] = model_data["model_id"]
        
        logger.info(f"Adding new model: {model_data}")
        success = curated_models_service.add_model(model_data)
        
        if success:
            return {
                "success": True,
                "message": f"Model {model_request.model_id} added successfully",
                "model": model_data
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model {model_request.model_id} already exists"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding model: {str(e)}"
        )


@router.put("/admin/models/{model_id}", response_model=dict)
async def update_curated_model(
    model_id: str,
    model_request: ModelRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing model in the curated list (Admin only)"""
    
    # TODO: Add admin role check when roles are implemented
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        model_data = model_request.dict()
        # Map model_id to id for the service
        model_data["id"] = model_data["model_id"]
        success = curated_models_service.update_model(model_id, model_data)
        
        if success:
            return {
                "success": True,
                "message": f"Model {model_id} updated successfully",
                "model": model_data
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating model: {str(e)}"
        )


@router.delete("/admin/models/{model_id}", response_model=dict)
async def delete_curated_model(
    model_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a model from the curated list (Admin only)"""
    
    # TODO: Add admin role check when roles are implemented
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        success = curated_models_service.delete_model(model_id)
        
        if success:
            return {
                "success": True,
                "message": f"Model {model_id} deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting model: {str(e)}"
        )


@router.patch("/admin/models/{model_id}/toggle", response_model=dict)
async def toggle_curated_model(
    model_id: str,
    toggle_request: ModelToggleRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Toggle a model's active status in the curated list (Admin only)"""
    
    # TODO: Add admin role check when roles are implemented
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        success = curated_models_service.toggle_model(model_id, toggle_request.is_active)
        
        if success:
            status_text = "activated" if toggle_request.is_active else "deactivated"
            return {
                "success": True,
                "message": f"Model {model_id} {status_text} successfully",
                "model_id": model_id,
                "is_active": toggle_request.is_active
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling model: {str(e)}"
        )


# Provider configuration endpoints
class ProviderConfigRequest(BaseModel):
    provider: str
    display_name: str
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    organization_id: Optional[str] = None
    is_active: bool = True
    max_requests_per_minute: int = 60
    max_tokens_per_request: int = 64000


class ProviderConfigResponse(BaseModel):
    id: Optional[int] = None
    provider: str
    display_name: str
    api_base_url: Optional[str] = None
    organization_id: Optional[str] = None
    is_active: bool
    max_requests_per_minute: int
    max_tokens_per_request: int
    last_sync_at: Optional[str] = None
    sync_error: Optional[str] = None
    has_api_key: bool = False


@router.get("/providers", response_model=List[ProviderConfigResponse])
async def get_provider_configs(
    current_user: User = Depends(get_current_active_user)
):
    """Get provider configurations (without API keys)"""
    # For now, return empty list - this would be implemented with database later
    return []


@router.post("/providers", response_model=dict)
async def create_or_update_provider_config(
    config: ProviderConfigRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Create or update provider configuration"""
    # For now, just return success - this would be implemented with database later
    return {
        "success": True,
        "message": f"Provider configuration for {config.display_name} saved successfully"
    }
