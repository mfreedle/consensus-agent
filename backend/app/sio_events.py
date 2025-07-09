import asyncio
import logging

from app.auth.dependencies import get_current_user_from_token
from app.database.connection import AsyncSessionLocal
from app.llm.orchestrator import LLMOrchestrator
from app.models.chat import ChatSession, Message
from app.models.file import File
from sqlalchemy import select

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
            # data = {"session_id": ..., "message": ..., "token": ..., "attached_file_ids": [...], "use_consensus": bool, "selected_models": [...]}
            session_id = data.get("session_id")
            message = data.get("message")
            token = data.get("token")
            attached_file_ids = data.get("attached_file_ids", [])
            use_consensus = data.get("use_consensus", False)
            selected_models = data.get("selected_models", [])
            
            logger.info(f"Socket.IO send_message: session_id={session_id} (type: {type(session_id)}), message_length={len(message) if message else 0}, use_consensus={use_consensus}, models={selected_models}")
            
            if not (message and token):
                await sio.emit('error', {'error': 'Missing required data'}, room=sid)
                return
            
            print(f"DEBUG Socket.IO: Received message with {len(attached_file_ids)} attached files, use_consensus: {use_consensus}, models: {selected_models}")
            
            # Authenticate user
            user = await get_current_user_from_token(token)
            if not user:
                logger.error(f"Socket.IO authentication failed for token: {token[:20]}...")
                await sio.emit('error', {'error': 'Unauthorized'}, room=sid)
                return
            
            logger.info(f"Socket.IO authenticated user: {user.id} ({user.username})")
            
            # Get database session
            async with AsyncSessionLocal() as db:
                try:
                    # Get or create session
                    session = None
                    if session_id:
                        # Convert session_id to int if it's a string
                        try:
                            session_id_int = int(session_id)
                        except (ValueError, TypeError):
                            await sio.emit('error', {'error': 'Invalid session ID format'}, room=sid)
                            return
                        
                        # Verify existing session belongs to user
                        session_stmt = select(ChatSession).where(
                            ChatSession.id == session_id_int,
                            ChatSession.user_id == user.id
                        )
                        session_result = await db.execute(session_stmt)
                        session = session_result.scalar_one_or_none()
                        
                        if not session:
                            logger.error(f"Chat session not found: session_id={session_id_int}, user_id={user.id}")
                            await sio.emit('error', {'error': 'Chat session not found'}, room=sid)
                            return
                        
                        # Update session_id to the integer value for consistency
                        session_id = session_id_int
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
                    
                    # Update session timestamp
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
                    
                    # Generate AI response
                    try:
                        # Combine user message with file context
                        full_prompt = message + file_context
                        
                        if use_consensus:
                            # Send initial processing status
                            await sio.emit('processing_status', {
                                "status": "analyzing",
                                "message": "Analyzing your request...",
                                "session_id": session_id
                            }, room=str(session_id))
                            
                            # Small delay to show status
                            await asyncio.sleep(0.5)
                            
                            # Send processing status
                            await sio.emit('processing_status', {
                                "status": "processing", 
                                "message": f"Consulting {len(selected_models)} AI models...",
                                "session_id": session_id
                            }, room=str(session_id))
                            
                            # Get consensus response from multiple models
                            consensus_result = await llm_orchestrator.generate_consensus(
                                prompt=full_prompt,
                                context=None
                            )
                            
                            # Debug: Log the consensus result content
                            logger.info(f"Consensus result type: {type(consensus_result.final_consensus)}")
                            logger.info(f"Consensus content preview: {consensus_result.final_consensus[:200]}...")
                            
                            # Send consensus building status
                            await sio.emit('processing_status', {
                                "status": "consensus",
                                "message": "Building consensus from model responses...",
                                "session_id": session_id
                            }, room=str(session_id))
                            
                            # Small delay to show status
                            await asyncio.sleep(0.5)
                            
                            # Send finalizing status
                            await sio.emit('processing_status', {
                                "status": "finalizing",
                                "message": "Finalizing response...",
                                "session_id": session_id
                            }, room=str(session_id))
                            
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
                            
                            # Validate response content before broadcasting
                            response_content = consensus_result.final_consensus
                            if response_content.strip().startswith('{') and response_content.strip().endswith('}'):
                                logger.warning("Detected JSON in consensus response, creating fallback")
                                response_content = f"""Based on consensus analysis from multiple AI models.

**Confidence:** {consensus_result.confidence_score * 100:.0f}%

This response synthesizes insights from multiple AI perspectives to provide a comprehensive answer."""
                            
                            # Broadcast AI response to room with consensus data
                            await sio.emit('new_message', {
                                "role": "assistant",
                                "content": response_content,
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
                            
                        else:
                            # Send processing status for single model
                            model = selected_models[0] if selected_models else "gpt-4o"
                            model_display = model.replace("-", " ").title()
                            
                            await sio.emit('processing_status', {
                                "status": "processing",
                                "message": f"Consulting {model_display}...",
                                "session_id": session_id
                            }, room=str(session_id))
                            
                            # Small delay to show status
                            await asyncio.sleep(0.3)
                            
                            # Get single model response
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
                            
                            # Save AI response for single model
                            ai_message = Message(
                                session_id=session_id,
                                role="assistant",
                                content=response.content,
                                model_used=model
                            )
                            
                            db.add(ai_message)
                            
                            await db.commit()
                            await db.refresh(ai_message)
                            
                            # Broadcast AI response to room without consensus data
                            await sio.emit('new_message', {
                                "role": "assistant",
                                "content": response.content,
                                "session_id": session_id,
                                "timestamp": ai_message.created_at.isoformat()
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
                        
                except Exception as db_error:
                    logger.error(f"Database error in send_message: {db_error}")
                    await sio.emit('error', {'error': 'Database error'}, room=sid)
                
        except Exception as e:
            logger.error(f"Error in send_message socket event: {e}")
            await sio.emit('error', {'error': 'Internal server error'}, room=sid)
