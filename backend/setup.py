#!/usr/bin/env python3
"""
Setup script for Agent Mark backend
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def setup_database():
    """Initialize the database with tables and seed data"""
    from app.config import settings
    from app.database.connection import init_db
    
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")

async def seed_models():
    """Seed the database with default LLM models"""
    from app.database.connection import AsyncSessionLocal
    from app.models.llm_model import LLMModel
    
    async with AsyncSessionLocal() as session:
        # Check if models already exist
        from sqlalchemy import select
        result = await session.execute(select(LLMModel))
        existing_models = result.scalars().all()
        
        if existing_models:
            print("Models already seeded.")
            return
        
        # Default models
        models = [
            LLMModel(
                provider="openai",
                model_name="gpt-4o",
                display_name="GPT-4o",
                description="Most capable OpenAI model for complex tasks",
                max_tokens=128000,
                supports_streaming=True,
                supports_function_calling=True,
                capabilities={"vision": True, "reasoning": True, "code": True}
            ),
            LLMModel(
                provider="openai", 
                model_name="gpt-4o-mini",
                display_name="GPT-4o Mini",
                description="Faster, cost-effective OpenAI model",
                max_tokens=128000,
                supports_streaming=True,
                supports_function_calling=True,
                capabilities={"vision": True, "reasoning": True, "code": True}
            ),
            LLMModel(
                provider="grok",
                model_name="grok-2",
                display_name="Grok-2",
                description="xAI's most capable model with real-time knowledge",
                max_tokens=131072,
                supports_streaming=True,
                supports_function_calling=False,
                capabilities={"real_time": True, "reasoning": True, "humor": True}
            ),
            LLMModel(
                provider="grok",
                model_name="grok-2-mini", 
                display_name="Grok-2 Mini",
                description="Faster Grok model for quick responses",
                max_tokens=131072,
                supports_streaming=True,
                supports_function_calling=False,
                capabilities={"real_time": True, "reasoning": True, "humor": True}
            )
        ]
        
        for model in models:
            session.add(model)
        
        await session.commit()
        print(f"Seeded {len(models)} LLM models")

async def create_default_user():
    """Create a default user for testing"""
    from app.auth.utils import get_password_hash
    from app.database.connection import AsyncSessionLocal
    from app.models.user import User
    
    async with AsyncSessionLocal() as session:
        # Check if default user exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Default user already exists.")
            return
        
        # Create default user
        user = User(
            username="admin",
            password_hash=get_password_hash("password123"),  # Change this!
            is_active=True
        )
        
        session.add(user)
        await session.commit()
        print("Created default user: admin / password123")

async def main():
    """Run setup tasks"""
    print("Setting up Agent Mark backend...")
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    print("Created uploads directory")
    
    # Setup database
    await setup_database()
    
    # Seed data
    await seed_models()
    await create_default_user()
    
    print("\nSetup completed successfully!")
    print("You can now start the server with: python -m app.main")
    print("Default login: admin / password123")

if __name__ == "__main__":
    asyncio.run(main())
