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
    
    # Google APIs - OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:3000/google-oauth-callback.html"
    
    # Google APIs - Service Account (for admin operations)
    google_service_account_file: str = ""
    google_project_id: str = ""
    google_client_email: str = ""
    
    # App Settings
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"
    port: int = 8000
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
