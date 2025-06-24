from app.auth.dependencies import get_current_user_from_token
from app.database.connection import get_db
from app.models.chat import Message
from sqlalchemy.ext.asyncio import AsyncSession


def register_sio_events(sio):
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
        # data = {"session_id": ..., "message": ..., "token": ...}
        session_id = data.get("session_id")
        message = data.get("message")
        token = data.get("token")
        if not (session_id and message and token):
            return
        # Authenticate user
        user = await get_current_user_from_token(token)
        if not user:
            await sio.emit('error', {'error': 'Unauthorized'}, room=sid)
            return
        # Save message to DB (simplified, add error handling as needed)
        db: AsyncSession = await get_db().__anext__()
        msg = Message(session_id=session_id, role="user", content=message)
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        # Broadcast to room
        await sio.emit('new_message', {"role": "user", "content": message, "session_id": session_id}, room=str(session_id))
