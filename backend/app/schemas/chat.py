from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# Chat session schemas
class ChatSessionBase(BaseModel):
    title: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    content: str
    role: str  # user, assistant, system

class MessageCreate(MessageBase):
    session_id: Optional[int] = None

class MessageResponse(MessageBase):
    id: int
    session_id: int
    model_used: Optional[str] = None
    consensus_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat request schemas
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    use_consensus: bool = True
    selected_models: Optional[List[str]] = None
    attached_file_ids: Optional[List[str]] = None

class ConsensusData(BaseModel):
    openai_response: str
    grok_response: str
    confidence_score: float
    final_consensus: str
    reasoning: str
    debate_points: List[str]

class ChatResponse(BaseModel):
    message: MessageResponse
    session: ChatSessionResponse
