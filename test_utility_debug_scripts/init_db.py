#!/usr/bin/env python3
"""
Database initialization script.
Creates default admin and user accounts for development.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.auth.utils import get_password_hash
from app.database.connection import engine
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_default_users():
    """Create default admin and user accounts."""
    
    # Default users to create
    default_users = [
        {
            "username": "admin",
            "password": "password123",
            "is_admin": True,
            "description": "Default admin account"
        },
        {
            "username": "user",
            "password": "user123",
            "is_admin": False,
            "description": "Default user account"
        },
        {
            "username": "testuser",
            "password": "test123",
            "is_admin": False,
            "description": "Test user account"
        }
    ]
    
    async with AsyncSession(engine) as db:
        try:
            for user_data in default_users:
                # Check if user already exists
                stmt = select(User).where(User.username == user_data["username"])
                result = await db.execute(stmt)
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"❓ User '{user_data['username']}' already exists - skipping")
                    continue
                
                # Create new user
                hashed_password = get_password_hash(user_data["password"])
                user = User(
                    username=user_data["username"],
                    password_hash=hashed_password,
                    is_active=True
                )
                
                db.add(user)
                print(f"✅ Created {user_data['description']}: {user_data['username']} / {user_data['password']}")
            
            await db.commit()
            print("\n🎉 Database initialization complete!")
            print("🌐 You can now login to http://localhost:3011 with any of the accounts above")
            
        except Exception as e:
            print(f"❌ Error creating default users: {e}")
            await db.rollback()
            raise


async def main():
    """Main initialization function."""
    print("🔧 Initializing database with default users...")
    print("=" * 50)
    
    try:
        await create_default_users()
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
