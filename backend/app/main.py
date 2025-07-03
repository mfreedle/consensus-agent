import os
from contextlib import asynccontextmanager
from pathlib import Path

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
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3010,http://localhost:3011").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
fastapi_app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
fastapi_app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
fastapi_app.include_router(files_router, prefix="/api/files", tags=["Files"])
fastapi_app.include_router(approval_router, prefix="/api/files", tags=["Document Approvals"])
fastapi_app.include_router(llm_router, prefix="/api/models", tags=["LLM Models"])
fastapi_app.include_router(google_router, prefix="/api/google", tags=["Google Drive"])

# Mount static files for frontend
frontend_build_path = Path(__file__).parent.parent.parent / "frontend" / "build"
if frontend_build_path.exists():
    fastapi_app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")

@fastapi_app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("APP_ENV", "development")
    }

# Catch-all route for frontend (must be last)
@fastapi_app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend files and fallback to index.html for SPA routing"""
    if path.startswith("api/"):
        # Let API routes handle themselves
        return {"error": "API endpoint not found"}
    
    frontend_build_path = Path(__file__).parent.parent.parent / "frontend" / "build"
    if not frontend_build_path.exists():
        return {"message": "Consensus Agent API is running", "status": "healthy"}
    
    # Try to serve the requested file
    requested_file = frontend_build_path / path
    if requested_file.exists() and requested_file.is_file():
        return FileResponse(str(requested_file))
    
    # Fallback to index.html for SPA routing
    index_file = frontend_build_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return {"message": "Consensus Agent API is running", "status": "healthy"}

# --- Socket.IO integration ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
register_sio_events(sio)
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=os.getenv("APP_ENV") == "development")