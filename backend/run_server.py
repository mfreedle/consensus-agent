#!/usr/bin/env python3
"""
Simple server startup script for the Consensus Agent backend
"""

import os
import sys

import uvicorn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Import the app after setting up the path
    from app.main import fastapi_app

    # Run the server
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
