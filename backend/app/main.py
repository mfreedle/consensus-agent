import os
from contextlib import asynccontextmanager

import socketio
from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.database.connection import init_db
from app.files.approval_router import router as approval_router
from app.files.router import router as files_router
from app.google.router import router as google_router
from app.llm.router import router as llm_router
from app.sio_events import register_sio_events
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# Create FastAPI app
fastapi_app = FastAPI(
    title="Consensus Agent - AI Chat Application",
    description="Multi-LLM consensus chat application with document management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
fastapi_app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
fastapi_app.include_router(chat_router, prefix="/chat", tags=["Chat"])
fastapi_app.include_router(files_router, prefix="/files", tags=["Files"])
fastapi_app.include_router(approval_router, prefix="/files", tags=["Document Approvals"])
fastapi_app.include_router(llm_router, prefix="/models", tags=["LLM Models"])
fastapi_app.include_router(google_router, prefix="/google", tags=["Google Drive"])

@fastapi_app.get("/")
async def root():
    return {"message": "Consensus Agent API is running", "status": "healthy"}

@fastapi_app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("APP_ENV", "development")
    }

# --- Socket.IO integration ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
register_sio_events(sio)
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=os.getenv("APP_ENV") == "development")