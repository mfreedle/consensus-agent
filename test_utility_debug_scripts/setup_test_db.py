#!/usr/bin/env python3
"""
Simple script to set up the test database with tables and data.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set the database URL to use the root database
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
db_path = os.path.join(root_dir, 'agent_mark.db')
os.environ['DATABASE_URL'] = f'sqlite+aiosqlite:///{db_path}'

from app.database.connection import init_db


async def main():
    """Initialize the database"""
    print("🔧 Setting up test database...")
    print(f"Database path: {db_path}")
    
    try:
        await init_db()
        print("✅ Database setup completed successfully!")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
