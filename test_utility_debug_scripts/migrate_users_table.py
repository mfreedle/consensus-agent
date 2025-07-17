#!/usr/bin/env python3
"""
Database migration script to add email column to users table.
This ensures compatibility with existing installations.
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.database.connection import engine


async def migrate_users_table():
    """Add email column to users table if it doesn't exist."""
    
    print("🔄 Starting users table migration...")
    
    try:
        async with AsyncSession(engine) as session:
            # Check if email column exists
            print("📋 Checking users table schema...")
            
            # For SQLite
            result = await session.execute(text("PRAGMA table_info(users)"))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'email' not in column_names:
                print("➕ Adding email column to users table...")
                await session.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
                await session.execute(text("CREATE INDEX idx_users_email ON users (email)"))
                await session.commit()
                print("✅ Email column added successfully")
            else:
                print("✅ Email column already exists")
        
        print("🎉 Users table migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


async def main():
    """Main migration function."""
    await migrate_users_table()


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main())
