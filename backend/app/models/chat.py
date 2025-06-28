from app.database.connection import Base
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    approvals = relationship("DocumentApproval", back_populates="chat_session")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    model_used = Column(String(50), nullable=True)
    
    # Consensus data for multi-LLM responses
    consensus_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
