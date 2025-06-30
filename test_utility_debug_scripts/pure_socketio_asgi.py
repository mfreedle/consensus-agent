import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print("Socket connected:", sid)

@sio.event
async def disconnect(sid):
    print("Socket disconnected:", sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pure_socketio_asgi:app", host="127.0.0.1", port=8000, reload=True)