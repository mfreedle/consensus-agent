import logging

from app.auth.dependencies import get_current_user_from_token
from app.database.connection import get_db
from app.llm.orchestrator import LLMOrchestrator
from app.models.chat import ChatSession, Message
from app.models.file import File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

def register_sio_events(sio):
    # Initialize LLM orchestrator
    llm_orchestrator = LLMOrchestrator()
    
    @sio.on('connect')
    async def connect(sid, environ):
        print(f"Socket connected: {sid}")

    @sio.on('disconnect')
    async def disconnect(sid):
        print(f"Socket disconnected: {sid}")

    @sio.on('join')
    async def join(sid, data):
        # data = {"session_id": ...}
        session_id = data.get("session_id")
        if session_id:
            await sio.enter_room(sid, str(session_id))
            print(f"Socket {sid} joined room {session_id}")

    @sio.on('send_message')
    async def send_message(sid, data):
        try:
            # data = {"session_id": ..., "message": ..., "token": ..., "attached_file_ids": [...]}
            session_id = data.get("session_id")
            message = data.get("message")
            token = data.get("token")
            attached_file_ids = data.get("attached_file_ids", [])
            
            if not (message and token):
                await sio.emit('error', {'error': 'Missing required data'}, room=sid)
                return
            
            print(f"DEBUG Socket.IO: Received message with {len(attached_file_ids)} attached files")
            
            # Authenticate user
            user = await get_current_user_from_token(token)
            if not user:
                await sio.emit('error', {'error': 'Unauthorized'}, room=sid)
                return
            
            # Get database session
            async for db in get_db():
                try:
                    # Get or create session
                    session = None
                    if session_id:
                        # Verify existing session belongs to user
                        session_stmt = select(ChatSession).where(
                            ChatSession.id == session_id,
                            ChatSession.user_id == user.id
                        )
                        session_result = await db.execute(session_stmt)
                        session = session_result.scalar_one_or_none()
                        
                        if not session:
                            await sio.emit('error', {'error': 'Chat session not found'}, room=sid)
                            return
                    else:
                        # Create new session
                        session = ChatSession(
                            user_id=user.id,
                            title=message[:50] + "..." if len(message) > 50 else message
                        )
                        db.add(session)
                        await db.commit()
                        await db.refresh(session)
                        session_id = session.id
                        
                        # Join the new session room
                        await sio.enter_room(sid, str(session_id))
                        
                        # Emit session created event
                        await sio.emit('session_created', {
                            'session_id': session_id,
                            'title': session.title
                        }, room=sid)
                    
                    # Save user message to DB
                    user_msg = Message(
                        session_id=session_id, 
                        role="user", 
                        content=message
                    )
                    db.add(user_msg)
                    await db.commit()
                    await db.refresh(user_msg)
                    
                    # Broadcast user message to room
                    await sio.emit('new_message', {
                        "role": "user", 
                        "content": message, 
                        "session_id": session_id,
                        "timestamp": user_msg.created_at.isoformat()
                    }, room=str(session_id))
                    
                    # Get attached files context if any
                    file_context = ""
                    if attached_file_ids:
                        print(f"DEBUG Socket.IO: Processing {len(attached_file_ids)} attached file IDs: {attached_file_ids}")
                        file_ids = [int(fid) for fid in attached_file_ids]
                        files_stmt = select(File).where(
                            File.id.in_(file_ids),
                            File.user_id == user.id
                        )
                        files_result = await db.execute(files_stmt)
                        files = files_result.scalars().all()
                        
                        if files:
                            print(f"DEBUG Socket.IO: Found {len(files)} attached files")
                            file_context = "\n\nAttached files context:\n"
                            for file in files:
                                print(f"DEBUG Socket.IO: Processing file: {file.original_filename}")
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
                    
                    # Generate AI response using consensus
                    try:
                        # Combine user message with file context
                        full_prompt = message + file_context
                        consensus_result = await llm_orchestrator.generate_consensus(
                            prompt=full_prompt,
                            context=None  # TODO: Add file context here
                        )
                        
                        # Save AI response with consensus data
                        ai_message = Message(
                            session_id=session_id,
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
                        
                        db.add(ai_message)
                        await db.commit()
                        await db.refresh(ai_message)
                        
                        # Broadcast AI response to room
                        await sio.emit('new_message', {
                            "role": "assistant",
                            "content": consensus_result.final_consensus,
                            "session_id": session_id,
                            "timestamp": ai_message.created_at.isoformat(),
                            "consensus": {
                                "openai_response": {
                                    "content": consensus_result.openai_response.content,
                                    "confidence": consensus_result.openai_response.confidence,
                                    "reasoning": consensus_result.openai_response.reasoning
                                },
                                "grok_response": {
                                    "content": consensus_result.grok_response.content,
                                    "confidence": consensus_result.grok_response.confidence,
                                    "reasoning": consensus_result.grok_response.reasoning
                                },
                                "final_consensus": consensus_result.final_consensus,
                                "confidence_score": consensus_result.confidence_score,
                                "reasoning": consensus_result.reasoning,
                                "debate_points": consensus_result.debate_points
                            }
                        }, room=str(session_id))
                        
                    except Exception as llm_error:
                        logger.error(f"Error generating AI response: {llm_error}")
                        
                        # Save error message
                        error_message = Message(
                            session_id=session_id,
                            role="assistant",
                            content=f"I'm sorry, I encountered an error while processing your request: {str(llm_error)}",
                            model_used="error"
                        )
                        db.add(error_message)
                        await db.commit()
                        await db.refresh(error_message)
                        
                        # Broadcast error message
                        await sio.emit('new_message', {
                            "role": "assistant",
                            "content": error_message.content,
                            "session_id": session_id,
                            "timestamp": error_message.created_at.isoformat()
                        }, room=str(session_id))
                    
                    # Break out of the async generator loop after successful processing
                    break
                    
                except Exception as db_error:
                    logger.error(f"Database error in send_message: {db_error}")
                    await sio.emit('error', {'error': 'Database error'}, room=sid)
                    break
                
        except Exception as e:
            logger.error(f"Error in send_message socket event: {e}")
            await sio.emit('error', {'error': 'Internal server error'}, room=sid)
