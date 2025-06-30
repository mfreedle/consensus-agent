import socketio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount the Socket.IO ASGI app
app.mount("/socket.io", socketio.ASGIApp(sio, other_asgi_app=app))

@sio.event
async def connect(sid, environ):
    print("Socket connected:", sid)

@sio.event
async def disconnect(sid):
    print("Socket disconnected:", sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("minimal_socketio_asgi:app", host="127.0.0.1", port=8000, reload=True)