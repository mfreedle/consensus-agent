from typing import List, Optional

from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.services.curated_models import curated_models_service
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


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
