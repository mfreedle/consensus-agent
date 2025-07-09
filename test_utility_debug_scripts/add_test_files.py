#!/usr/bin/env python3
"""
Script to add test files to the database for testing knowledge base integration.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set the database URL to use the root database
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
db_path = os.path.join(root_dir, 'agent_mark.db')
os.environ['DATABASE_URL'] = f'sqlite+aiosqlite:///{db_path}'

from app.database.connection import AsyncSessionLocal
from app.models.file import File
from app.models.user import User
from sqlalchemy import select


async def add_test_files():
    """Add some test files to the database"""
    
    # Test file data
    test_files = [
        {
            "filename": "test_document_1.txt",
            "original_filename": "Project Overview.txt",
            "file_type": "text",
            "file_size": 1024,
            "mime_type": "text/plain",
            "extracted_text": """
# Project Overview

This is a comprehensive overview of our Consensus Agent project.

## Key Features
- Multi-agent AI consensus system
- Knowledge base integration
- File attachment capabilities
- Real-time chat interface

## Technical Stack
- Backend: FastAPI with Python
- Frontend: React with TypeScript
- Database: PostgreSQL (production) / SQLite (development)
- AI Models: OpenAI GPT-4, Grok, DeepSeek

## Current Status
The system supports multiple AI models working together to provide consensus-based responses.
Users can upload files to a knowledge base that is automatically accessible to AI models.
""",
            "is_processed": True
        },
        {
            "filename": "test_document_2.md",
            "original_filename": "API Documentation.md", 
            "file_type": "markdown",
            "file_size": 2048,
            "mime_type": "text/markdown",
            "extracted_text": """
# API Documentation

## Chat Endpoints

### POST /api/chat/send
Send a message to the AI consensus system.

**Request Body:**
```json
{
  "message": "string",
  "session_id": "string",
  "attached_files": ["file_id_1", "file_id_2"]
}
```

**Response:**
```json
{
  "response": "string",
  "consensus_data": {...},
  "models_used": ["gpt-4", "grok"]
}
```

### GET /api/files
List user's uploaded files.

### POST /api/files/upload
Upload a file to the knowledge base.

## Authentication
All endpoints require Bearer token authentication.
""",
            "is_processed": True
        },
        {
            "filename": "test_document_3.txt",
            "original_filename": "Configuration Guide.txt",
            "file_type": "text", 
            "file_size": 1536,
            "mime_type": "text/plain",
            "extracted_text": """
# Configuration Guide

## Environment Variables

### Database Configuration
- DATABASE_URL: Connection string for PostgreSQL/SQLite
- For PostgreSQL: postgresql+asyncpg://user:pass@host:port/db
- For SQLite: sqlite+aiosqlite:///./database.db

### AI Model Configuration
- OPENAI_API_KEY: Your OpenAI API key
- GROK_API_KEY: Your xAI Grok API key  
- DEEPSEEK_API_KEY: Your DeepSeek API key

### Security Settings
- JWT_SECRET_KEY: Secret key for JWT token signing
- JWT_ALGORITHM: Algorithm for JWT (default: HS256)
- JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time

## Model Management
Models are stored in the llm_models table and can be enabled/disabled via the admin interface.
""",
            "is_processed": True
        }
    ]
    
    async with AsyncSessionLocal() as db:
        print("📝 Adding test files to database...")
        
        # Get the admin user (ID: 1)
        user_stmt = select(User).where(User.username == "admin")
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("❌ Admin user not found")
            return False
        
        print(f"✅ Found user: {user.username} (ID: {user.id})")
        
        # Add test files
        for file_data in test_files:
            file = File(
                user_id=user.id,
                filename=file_data["filename"],
                original_filename=file_data["original_filename"],
                file_path=f"./uploads/{file_data['filename']}",
                file_type=file_data["file_type"],
                file_size=file_data["file_size"],
                mime_type=file_data["mime_type"],
                extracted_text=file_data["extracted_text"],
                is_processed=file_data["is_processed"],
                uploaded_at=datetime.utcnow()
            )
            
            db.add(file)
            print(f"   • Added: {file_data['original_filename']}")
        
        await db.commit()
        print(f"✅ Successfully added {len(test_files)} test files!")
        return True

async def main():
    """Add test files"""
    print("🧪 Adding Test Files to Database\n")
    print("=" * 50)
    
    try:
        success = await add_test_files()
        
        if success:
            print("\n🎉 Test files added successfully!")
            print("📄 Files in knowledge base:")
            print("   • Project Overview.txt - Project details and features")
            print("   • API Documentation.md - API endpoint documentation")  
            print("   • Configuration Guide.txt - Setup and config instructions")
            print("\nYou can now run the knowledge base integration test.")
        else:
            print("\n❌ Failed to add test files")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
