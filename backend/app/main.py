import os
from contextlib import asynccontextmanager

from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.database.connection import init_db
from app.files.router import router as files_router
from app.google.router import router as google_router
from app.llm.router import router as llm_router
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

# Load environment variables
load_dotenv()

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title="Consensus Agent - AI Chat Application",
    description="Multi-LLM consensus chat application with document management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(files_router, prefix="/files", tags=["Files"])
app.include_router(llm_router, prefix="/models", tags=["LLM Models"])
app.include_router(google_router, prefix="/google", tags=["Google Drive"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Consensus Agent API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("APP_ENV", "development")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("APP_ENV") == "development"
    )
