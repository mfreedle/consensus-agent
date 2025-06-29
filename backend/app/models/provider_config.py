from app.database.connection import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func


class ProviderConfig(Base):
    """Model for storing AI provider configurations and API keys"""
    __tablename__ = "provider_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, unique=True)  # openai, grok, deepseek, anthropic
    display_name = Column(String(100), nullable=False)  # OpenAI, Grok, DeepSeek, Anthropic
    
    # API Configuration
    api_key = Column(Text, nullable=True)  # Encrypted API key
    api_base_url = Column(String(500), nullable=True)  # Base URL for API
    organization_id = Column(String(100), nullable=True)  # For OpenAI org ID
    
    # Provider settings
    is_active = Column(Boolean, default=True)
    max_requests_per_minute = Column(Integer, default=60)
    max_tokens_per_request = Column(Integer, default=4000)
    
    # Model sync settings
    auto_sync_models = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    sync_error = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
