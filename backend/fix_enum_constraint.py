#!/usr/bin/env python3
"""
Fix the database enum constraint to match Python enum values.
This fixes the ApprovalStatus enum to use lowercase values.
"""

import asyncio
from app.database.connection import get_db
from sqlalchemy import text

async def fix_enum_constraint():
    async for db in get_db():
        try:
            print("🔧 Fixing ApprovalStatus enum constraint...")
            
            # First, check if we're using SQLite (which doesn't have strict enum constraints)
            result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='document_approvals'"))
            is_sqlite = result.fetchone() is not None
            
            if is_sqlite:
                print("✅ Using SQLite - enum constraint is flexible")
                # For SQLite, we just need to make sure all data uses lowercase
                # Let's verify our data is all lowercase now
                result = await db.execute(text("SELECT DISTINCT status FROM document_approvals"))
                statuses = [row[0] for row in result.fetchall()]
                print(f"📊 Current status values: {statuses}")
                
                # Check if any uppercase values remain
                uppercase_statuses = [s for s in statuses if s != s.lower()]
                if uppercase_statuses:
                    print(f"⚠️ Found uppercase statuses: {uppercase_statuses}")
                    # Fix any remaining uppercase values
                    for status in uppercase_statuses:
                        await db.execute(text(f"UPDATE document_approvals SET status = '{status.lower()}' WHERE status = '{status}'"))
                    await db.commit()
                    print("✅ Fixed remaining uppercase values")
                else:
                    print("✅ All status values are already lowercase")
            else:
                # For PostgreSQL/MySQL, we'd need to drop and recreate the enum type
                print("⚠️ Non-SQLite database detected - enum constraint fix may require manual intervention")
            
            # Test that we can now query the data
            print("\n🧪 Testing query after fix...")
            result = await db.execute(text("SELECT id, status, title FROM document_approvals ORDER BY id DESC LIMIT 3"))
            records = result.fetchall()
            print("✅ Query successful! Recent records:")
            for record in records:
                print(f"  ID: {record[0]}, Status: {record[1]}, Title: {record[2][:30]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
        break

if __name__ == "__main__":
    asyncio.run(fix_enum_constraint())
