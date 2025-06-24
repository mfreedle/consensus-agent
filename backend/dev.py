#!/usr/bin/env python3
"""
Development server for Agent Mark backend
"""

import os
from pathlib import Path

import uvicorn

if __name__ == "__main__":
    # Set development environment
    os.environ.setdefault("APP_ENV", "development")
    
    # Load environment variables from .env if it exists
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
