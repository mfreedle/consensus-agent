from fastapi import FastAPI
from fastapi_socketio import SocketManager

app = FastAPI()
sio = SocketManager(app=app)

@sio.on('connect')
async def connect(sid, environ):
    print(f"Socket connected: {sid}")

@sio.on('disconnect')
async def disconnect(sid):
    print(f"Socket disconnected: {sid}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("minimal_socketio_test:app", host="127.0.0.1", port=8000, reload=True)