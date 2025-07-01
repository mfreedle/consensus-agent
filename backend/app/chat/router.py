from typing import List, Optional

from app.auth.dependencies import get_current_active_user
from app.database.connection import get_db
from app.llm.orchestrator import llm_orchestrator
from app.models.chat import ChatSession, Message
from app.models.file import File
from app.models.user import User
from app.schemas.chat import (ChatRequest, ChatResponse, ChatSessionCreate,
                              ChatSessionResponse, ConsensusData,
                              MessageCreate, MessageResponse)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session"""
    
    session = ChatSession(
        user_id=current_user.id,
        title=session_data.title or "New Chat"
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    
    # Use COALESCE to fall back to created_at when updated_at is NULL
    # This handles existing sessions that don't have updated_at set
    from sqlalchemy import func
    order_field = func.coalesce(ChatSession.updated_at, ChatSession.created_at)
    
    stmt = select(ChatSession).where(
        ChatSession.user_id == current_user.id
    ).order_by(desc(order_field))
    
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific chat session"""
    
    stmt = select(ChatSession).where(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    )
    
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a chat session"""
    
    # Verify session belongs to user
    session_stmt = select(ChatSession).where(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    )
    session_result = await db.execute(session_stmt)
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get messages
    messages_stmt = select(Message).where(
        Message.session_id == session_id
    ).order_by(Message.created_at)
    
    messages_result = await db.execute(messages_stmt)
    messages = messages_result.scalars().all()
    
    return messages

@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response"""
    
    # Get or create session
    session = None
    if chat_request.session_id:
        stmt = select(ChatSession).where(
            ChatSession.id == chat_request.session_id,
            ChatSession.user_id == current_user.id
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
    else:
        # Create new session
        session = ChatSession(
            user_id=current_user.id,
            title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
    
    # Get attached files context if any
    file_context = ""
    if chat_request.attached_file_ids:
        print(f"DEBUG: Received attached file IDs: {chat_request.attached_file_ids}")
        file_ids = [int(fid) for fid in chat_request.attached_file_ids]
        files_stmt = select(File).where(
            File.id.in_(file_ids),
            File.user_id == current_user.id
        )
        files_result = await db.execute(files_stmt)
        files = files_result.scalars().all()
        
        if files:
            print(f"DEBUG: Found {len(files)} attached files")
            file_context = "\n\nAttached files context:\n"
            for file in files:
                print(f"DEBUG: Processing file: {file.original_filename}")
                file_context += f"\n--- {file.original_filename} ---\n"
                file_context += f"\n--- {file.original_filename} ---\n"
                if file.extracted_text:
                    # Limit file content to prevent context overflow
                    content = file.extracted_text[:5000]
                    if len(file.extracted_text) > 5000:
                        content += "\n... (content truncated)"
                    file_context += content
                else:
                    file_context += "(File not yet processed or could not extract text)"
                file_context += "\n"
    
    # Save user message
    user_message = Message(
        session_id=session.id,
        role="user",
        content=chat_request.message
    )
    db.add(user_message)
    
    # Update session timestamp when new message is added
    from sqlalchemy import func
    session.updated_at = func.now()
    
    await db.commit()
    await db.refresh(user_message)
    
    # Generate AI response
    try:
        # Combine user message with file context
        full_prompt = chat_request.message + file_context
        
        if chat_request.use_consensus:
            # Get consensus response from multiple models
            consensus_result = await llm_orchestrator.generate_consensus(
                prompt=full_prompt,
                context=None
            )
            
            # Save AI response with consensus data
            ai_message = Message(
                session_id=session.id,
                role="assistant",
                content=consensus_result.final_consensus,
                model_used="consensus",
                consensus_data={
                    "openai_response": consensus_result.openai_response.dict(),
                    "grok_response": consensus_result.grok_response.dict(),
                    "confidence_score": consensus_result.confidence_score,
                    "reasoning": consensus_result.reasoning,
                    "debate_points": consensus_result.debate_points
                }
            )
        else:
            # Get single model response (default to OpenAI)
            model = chat_request.selected_models[0] if chat_request.selected_models else "gpt-4o"
            if model.startswith("gpt"):
                response = await llm_orchestrator.get_openai_response(
                    prompt=full_prompt,
                    model=model
                )
            else:
                response = await llm_orchestrator.get_grok_response(
                    prompt=full_prompt,
                    model=model
                )
            
            ai_message = Message(
                session_id=session.id,
                role="assistant",
                content=response.content,
                model_used=model
            )
        
        db.add(ai_message)
        
        # Update session timestamp when AI response is added
        from sqlalchemy import func
        session.updated_at = func.now()
        
        await db.commit()
        await db.refresh(ai_message)
        await db.refresh(session)
        
        return ChatResponse(
            message=ai_message,
            session=session
        )
        
    except Exception as e:
        # Save error message
        error_message = Message(
            session_id=session.id,
            role="assistant",
            content=f"I'm sorry, I encountered an error while processing your request: {str(e)}",
            model_used="error"
        )
        db.add(error_message)
        
        # Update session timestamp for error messages too
        from sqlalchemy import func
        session.updated_at = func.now()
        
        await db.commit()
        await db.refresh(error_message)
        
        return ChatResponse(
            message=error_message,
            session=session
        )

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    
    stmt = select(ChatSession).where(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    )
    
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    await db.delete(session)
    await db.commit()
    
    return {"message": "Chat session deleted successfully"}
