from app.database.connection import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class LLMModel(Base):
    __tablename__ = "llm_models"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)  # openai, grok
    model_name = Column(String(100), nullable=False)  # gpt-4o, grok-2, etc.
    display_name = Column(String(100), nullable=False)  # Human readable name
    description = Column(String(500), nullable=True)
    
    # Model configuration
    is_active = Column(Boolean, default=True)
    max_tokens = Column(Integer, nullable=True)
    supports_streaming = Column(Boolean, default=True)
    supports_function_calling = Column(Boolean, default=False)
    
    # Capabilities and metadata
    capabilities = Column(JSON, nullable=True)  # Store model-specific capabilities
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
