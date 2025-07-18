import asyncio
import logging

from app.auth.dependencies import get_current_user_from_token
from app.config import settings
from app.database.connection import AsyncSessionLocal
from app.google.service import GoogleDriveService
from app.llm.google_drive_context import GoogleDriveContextManager
from app.llm.google_drive_tools import GoogleDriveTools
from app.llm.orchestrator import LLMOrchestrator
from app.models.chat import ChatSession, Message
from app.models.file import File
from sqlalchemy import select

logger = logging.getLogger(__name__)

def register_sio_events(sio):
    # Initialize LLM orchestrator with Google Drive tools
    llm_orchestrator = LLMOrchestrator()
    
    # Initialize Google Drive integration
    google_service = GoogleDriveService(settings)
    google_drive_context_manager = GoogleDriveContextManager(google_service)
    google_drive_tools = GoogleDriveTools(google_service)
    
    # Set Google Drive tools in the orchestrator for function calling
    llm_orchestrator.set_google_drive_tools(google_drive_tools)
    
    async def build_conversation_context(db, session_id, max_messages: int = 25) -> str:
        """Build conversation context from recent messages in the session"""
        try:
            # Ensure session_id is an integer
            if hasattr(session_id, '__int__'):
                actual_id = int(session_id)
            elif isinstance(session_id, int):
                actual_id = session_id
            else:
                actual_id = int(str(session_id))
            
            # Get recent messages from the session (excluding the current message being processed)
            messages_stmt = select(Message).where(
                Message.session_id == actual_id
            ).order_by(Message.created_at.desc()).limit(max_messages)
            
            messages_result = await db.execute(messages_stmt)
            messages = list(messages_result.scalars().all())
            
            if not messages:
                return ""
            
            # Reverse to get chronological order
            messages.reverse()
            
            # Build context string with smart truncation
            context_parts = ["Previous conversation context:"]
            total_length = 0
            max_context_length = 50000  # Increased to 50k chars (~12.5k tokens) - still very conservative
            
            for msg in messages:
                role_label = "User" if msg.role == "user" else "Assistant"
                # Allow much longer individual messages for better context preservation
                content = msg.content[:2000] + "..." if len(msg.content) > 2000 else msg.content
                message_part = f"{role_label}: {content}"
                
                # Check if adding this message would exceed our limit
                if total_length + len(message_part) > max_context_length:
                    break
                    
                context_parts.append(message_part)
                total_length += len(message_part)
            
            context = "\n".join(context_parts)
            logger.info(f"Built conversation context with {len(context_parts)-1} messages, {total_length} chars")
            return context
            
        except Exception as e:
            logger.error(f"Error building conversation context: {e}")
            return ""
    
    @sio.on('connect')
    async def connect(sid, environ, auth):
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
                    attached_files_context = ""
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
                            attached_files_context = "\n\nAttached files for this message:\n"
                            for file in files:
                                print(f"DEBUG Socket.IO: Processing attached file: {file.original_filename}")
                                attached_files_context += f"\n--- {file.original_filename} ---\n"
                                extracted_text = getattr(file, 'extracted_text', None)
                                if extracted_text:
                                    # Limit file content to prevent context overflow
                                    content = extracted_text[:5000]
                                    if len(extracted_text) > 5000:
                                        content += "\n... (content truncated)"
                                    attached_files_context += content
                                else:
                                    attached_files_context += "(File not yet processed or could not extract text)"
                                attached_files_context += "\n"
                    
                    # Get ALL knowledge base files for this user (for persistent context)
                    knowledge_base_context = ""
                    all_files_stmt = select(File).where(
                        File.user_id == user.id,
                        File.is_processed.is_(True),
                        File.extracted_text.is_not(None)
                    ).order_by(File.uploaded_at.desc())
                    
                    all_files_result = await db.execute(all_files_stmt)
                    all_files = all_files_result.scalars().all()
                    
                    if all_files:
                        print(f"DEBUG Socket.IO: Found {len(all_files)} knowledge base files")
                        knowledge_base_context = "\n\nKnowledge Base Files (available for reference):\n"
                        total_kb_length = 0
                        max_kb_length = 15000  # Limit knowledge base context to prevent overflow
                        
                        for file in all_files:
                            extracted_text = getattr(file, 'extracted_text', None)
                            if extracted_text:
                                # Skip files that were already included as attachments
                                if attached_file_ids and str(file.id) in attached_file_ids:
                                    continue
                                    
                                # Limit individual file content and check total length
                                content = extracted_text[:3000]
                                if len(extracted_text) > 3000:
                                    content += "\n... (content truncated)"
                                
                                file_entry = f"\n--- {file.original_filename} ---\n{content}\n"
                                
                                if total_kb_length + len(file_entry) > max_kb_length:
                                    knowledge_base_context += "\n... (additional files available but truncated to prevent context overflow)\n"
                                    break
                                    
                                knowledge_base_context += file_entry
                                total_kb_length += len(file_entry)
                    
                    # Combine all file contexts
                    file_context = attached_files_context + knowledge_base_context
                    
                    # Add Google Drive context if user has Google Drive connected
                    google_drive_context = ""
                    try:
                        google_drive_context = await google_drive_context_manager.get_google_drive_context(user, limit=5)
                        if google_drive_context:
                            logger.info(f"Added Google Drive context: {len(google_drive_context)} characters")
                    except Exception as e:
                        logger.warning(f"Could not get Google Drive context: {e}")
                    
                    # Combine all contexts
                    full_context = file_context + google_drive_context
                    
                    # Generate AI response
                    try:
                        # Build conversation context from previous messages  
                        # Get the actual session ID value
                        actual_session_id = session_id if hasattr(session_id, '__int__') or isinstance(session_id, int) else int(str(session_id))
                        conversation_context = await build_conversation_context(db, actual_session_id)
                        
                        # Combine all context with the full context
                        combined_context = conversation_context + full_context
                        
                        # Combine user message with full context
                        full_prompt = message + full_context
                        
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
                            
                            # Get consensus response from dynamically selected models with their tool capabilities
                            consensus_result = await llm_orchestrator.generate_consensus_dynamic(
                                prompt=full_prompt,
                                selected_models=selected_models,
                                context=combined_context
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
                            model = selected_models[0] if selected_models else "gpt-4.1-mini"  # Use gpt-4.1-mini for better function calling
                            model_display = model.replace("-", " ").title()
                            
                            await sio.emit('processing_status', {
                                "status": "processing",
                                "message": f"Consulting {model_display}...",
                                "session_id": session_id
                            }, room=str(session_id))
                            
                            # Small delay to show status
                            await asyncio.sleep(0.3)
                            
                            # Get single model response with provider-specific built-in tools
                            if model.startswith("gpt"):
                                response = await llm_orchestrator.get_openai_response_with_builtin_tools(
                                    prompt=full_prompt,
                                    model=model,
                                    context=combined_context
                                )
                            elif model.startswith("grok"):
                                response = await llm_orchestrator.get_grok_response_with_tools(
                                    prompt=full_prompt,
                                    model=model,
                                    context=combined_context
                                )
                            elif model.startswith("claude"):
                                response = await llm_orchestrator.get_claude_response_with_tools(
                                    prompt=full_prompt,
                                    model=model,
                                    context=combined_context
                                )
                            elif model.startswith("deepseek"):
                                response = await llm_orchestrator.get_deepseek_response_with_tools(
                                    prompt=full_prompt,
                                    model=model,
                                    context=combined_context
                                )
                            else:
                                # Fallback for unknown providers
                                response = await llm_orchestrator.get_grok_response(
                                    prompt=full_prompt,
                                    model=model,
                                    context=combined_context
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
                        logger.error(f"Session ID: {session_id}, Message length: {len(message)}")
                        logger.error(f"Use consensus: {use_consensus}, Models: {selected_models}")
                        
                        # Save error message
                        error_message = Message(
                            session_id=session_id,
                            role="assistant",
                            content="I'm sorry, I encountered an error while processing your request. Please try again.",
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
