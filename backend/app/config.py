import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./agent_mark.db"
    
    # JWT
    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str = ""
    openai_org_id: str = ""
    
    # Grok/xAI
    grok_api_key: str = ""
    
    # DeepSeek
    deepseek_api_key: str = ""
    
    # Anthropic
    anthropic_api_key: str = ""
    
    # Google APIs - OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    
    # Google APIs - Service Account (for admin operations)
    google_service_account_file: str = ""
    google_project_id: str = ""
    google_client_email: str = ""
    
    # App Settings
    app_env: str = "development"
    cors_origins: str = "http://localhost:3010"
    port: int = 8000
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def google_redirect_uri_resolved(self) -> str:
        """Get the appropriate Google OAuth redirect URI based on environment"""
        if self.google_redirect_uri:
            return self.google_redirect_uri
        
        try:
            # Auto-detect based on environment
            # Check for Railway environment
            railway_env = os.getenv('RAILWAY_ENVIRONMENT')
            railway_url = os.getenv('RAILWAY_STATIC_URL') or os.getenv('RAILWAY_PUBLIC_DOMAIN')
            
            if railway_env or railway_url or self.app_env == "production" or "railway.app" in self.cors_origins:
                return "https://consensus-agent.up.railway.app/google-oauth-callback.html"
            else:
                return "http://localhost:3010/google-oauth-callback.html"
        except Exception:
            # Fallback to localhost if there's any error
            return "http://localhost:3010/google-oauth-callback.html"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
