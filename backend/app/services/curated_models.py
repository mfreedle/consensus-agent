"""
Curated models service for managing the approved model list
"""
import json
from pathlib import Path
from typing import Dict, List

# Default curated models
DEFAULT_CURATED_MODELS = [
    # Grok models
    {
        "id": "grok-3-latest",
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
        "id": "grok-3-fast-latest",
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
        "id": "grok-3-mini-latest",
        "provider": "grok",
        "display_name": "Grok 3 Mini Latest",
        "description": "Compact version of Grok 3 for efficient tasks",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": False,
        "supports_vision": False,
        "context_window": 64000,
        "capabilities": {
            "reasoning": "medium",
            "creativity": "medium",
            "efficiency": "high"
        }
    },
    {
        "id": "grok-3-mini-fast-latest",
        "provider": "grok",
        "display_name": "Grok 3 Mini Fast Latest",
        "description": "Fastest and most efficient Grok 3 variant",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": False,
        "supports_vision": False,
        "context_window": 64000,
        "capabilities": {
            "reasoning": "medium",
            "speed": "high",
            "efficiency": "high"
        }
    },
    # OpenAI models
    {
        "id": "gpt-4.1",
        "provider": "openai",
        "display_name": "GPT-4.1",
        "description": "Enhanced GPT-4 with improved reasoning capabilities",
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
        "id": "gpt-4.1-mini",
        "provider": "openai",
        "display_name": "GPT-4.1 Mini",
        "description": "Efficient version of GPT-4.1 for faster responses",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": True,
        "supports_vision": True,
        "context_window": 128000,
        "capabilities": {
            "reasoning": "high",
            "creativity": "medium",
            "efficiency": "high"
        }
    },
    {
        "id": "o3",
        "provider": "openai",
        "display_name": "O3",
        "description": "OpenAI's latest reasoning model with advanced problem-solving",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": True,
        "supports_vision": False,
        "context_window": 200000,
        "capabilities": {
            "reasoning": "very_high",
            "math": "very_high",
            "code": "very_high",
            "science": "very_high"
        }
    },
    {
        "id": "o3-mini",
        "provider": "openai",
        "display_name": "O3 Mini",
        "description": "Compact version of O3 for efficient reasoning tasks",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": True,
        "supports_vision": False,
        "context_window": 128000,
        "capabilities": {
            "reasoning": "high",
            "math": "high",
            "efficiency": "high"
        }
    },
    # DeepSeek models
    {
        "id": "deepseek-chat",
        "provider": "deepseek",
        "display_name": "DeepSeek Chat",
        "description": "DeepSeek's conversational AI model",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": True,
        "supports_vision": False,
        "context_window": 64000,
        "capabilities": {
            "reasoning": "high",
            "creativity": "high",
            "conversation": "high"
        }
    },
    {
        "id": "deepseek-reasoner",
        "provider": "deepseek",
        "display_name": "DeepSeek Reasoner",
        "description": "DeepSeek's advanced reasoning model",
        "is_active": True,
        "supports_streaming": True,
        "supports_function_calling": True,
        "supports_vision": False,
        "context_window": 64000,
        "capabilities": {
            "reasoning": "very_high",
            "math": "high",
            "logic": "very_high"
        }
    }
]

class CuratedModelsService:
    """Service for managing curated models list"""
    
    def __init__(self):
        # Use relative path from the current working directory
        self.config_dir = Path("config") 
        self.config_file = self.config_dir / "curated_models.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def get_models(self) -> List[Dict]:
        """Get all curated models"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, return defaults
                return DEFAULT_CURATED_MODELS.copy()
        else:
            # First time - create file with defaults
            self.save_models(DEFAULT_CURATED_MODELS)
            return DEFAULT_CURATED_MODELS.copy()
    
    def save_models(self, models: List[Dict]) -> None:
        """Save curated models to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(models, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save curated models: {e}")
    
    def add_model(self, model_data: Dict) -> bool:
        """Add a new model to the curated list"""
        models = self.get_models()
        
        # Check if model already exists
        if any(m["id"] == model_data["id"] for m in models):
            return False
        
        models.append(model_data)
        self.save_models(models)
        return True
    
    def update_model(self, model_id: str, model_data: Dict) -> bool:
        """Update an existing model"""
        models = self.get_models()
        
        for i, model in enumerate(models):
            if model["id"] == model_id:
                models[i] = model_data
                self.save_models(models)
                return True
        
        return False
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a model from the curated list"""
        models = self.get_models()
        original_length = len(models)
        
        models = [m for m in models if m["id"] != model_id]
        
        if len(models) < original_length:
            self.save_models(models)
            return True
        
        return False
    
    def toggle_model(self, model_id: str, is_active: bool) -> bool:
        """Toggle a model's active status"""
        models = self.get_models()
        
        for model in models:
            if model["id"] == model_id:
                model["is_active"] = is_active
                self.save_models(models)
                return True
        
        return False

# Global instance
curated_models_service = CuratedModelsService()
