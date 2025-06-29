from app.database.connection import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func


class LLMModel(Base):
    __tablename__ = "llm_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(100), nullable=False)  # gpt-4o, grok-2, etc.
    provider = Column(String(50), nullable=False)  # openai, grok, deepseek, anthropic
    display_name = Column(String(100), nullable=False)  # Human readable name
    description = Column(String(500), nullable=True)
    
    # Model capabilities
    max_tokens = Column(Integer, nullable=True)
    supports_streaming = Column(Boolean, default=True)
    supports_function_calling = Column(Boolean, default=False)
    supports_vision = Column(Boolean, default=False)
    context_window = Column(Integer, nullable=True)
    
    # Pricing (per 1K tokens)
    input_price_per_1k = Column(Float, nullable=True)
    output_price_per_1k = Column(Float, nullable=True)
    
    # Model status
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)  # From provider API
    
    # Capabilities and metadata
    capabilities = Column(JSON, nullable=True)  # Store model-specific capabilities
    provider_metadata = Column(JSON, nullable=True)  # Raw data from provider
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
