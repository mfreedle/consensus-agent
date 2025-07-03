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

@fastapi_app.get("/api/debug/users")
async def debug_users():
    """Debug endpoint to check what users exist in the database"""
    from app.database.connection import get_db
    from app.models.user import User
    from sqlalchemy import select
    
    async for db in get_db():
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        return {
            "total_users": len(users),
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "password_hash_length": len(user.password_hash) if user.password_hash else 0
                }
                for user in users
            ]
        }

@fastapi_app.get("/api/debug/test-password")
async def debug_test_password():
    """Debug endpoint to test password verification"""
    from app.auth.utils import get_password_hash, verify_password
    from app.database.connection import get_db
    from app.models.user import User
    from sqlalchemy import select
    
    test_password = "password123"
    
    async for db in get_db():
        # Get the admin user
        result = await db.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"error": "Admin user not found"}
        
        # Test password verification
        is_valid = verify_password(test_password, user.password_hash)
        
        # Generate a fresh hash for comparison
        fresh_hash = get_password_hash(test_password)
        fresh_is_valid = verify_password(test_password, fresh_hash)
        
        return {
            "user_exists": True,
            "stored_hash_length": len(user.password_hash),
            "test_password": test_password,
            "password_verification_result": is_valid,
            "fresh_hash_verification": fresh_is_valid,
            "fresh_hash_sample": fresh_hash[:20] + "..." if fresh_hash else None
        }

@fastapi_app.post("/api/debug/reset-admin-password")
async def debug_reset_admin_password():
    """Debug endpoint to reset admin password with fresh hash"""
    from app.auth.utils import get_password_hash, verify_password
    from app.database.connection import get_db
    from app.models.user import User
    from sqlalchemy import select
    
    new_password = "password123"
    
    async for db in get_db():
        # Get the admin user
        result = await db.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"error": "Admin user not found"}
        
        # Generate fresh password hash
        new_hash = get_password_hash(new_password)
        
        # Update user password
        user.password_hash = new_hash
        await db.commit()
        
        # Verify the new hash works
        verification_test = verify_password(new_password, new_hash)
        
        return {
            "success": True,
            "message": "Admin password reset successfully",
            "new_hash_length": len(new_hash),
            "verification_test": verification_test,
            "password": new_password
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