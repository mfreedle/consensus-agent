#!/usr/bin/env python3
"""
Fix enum values in document_approvals table to match Python enum definitions.
"""

import asyncio
from app.database.connection import get_db
from sqlalchemy import text

async def fix_enum_values():
    async for db in get_db():
        print("🔧 Fixing enum values in document_approvals table...")
        
        # Update PENDING to pending
        result = await db.execute(text("UPDATE document_approvals SET status = 'pending' WHERE status = 'PENDING'"))
        print(f"✅ Updated {result.rowcount} records from PENDING to pending")
        
        # Update any other uppercase values
        result = await db.execute(text("UPDATE document_approvals SET status = 'rejected' WHERE status = 'REJECTED'"))
        print(f"✅ Updated {result.rowcount} records from REJECTED to rejected")
        
        result = await db.execute(text("UPDATE document_approvals SET status = 'expired' WHERE status = 'EXPIRED'"))
        print(f"✅ Updated {result.rowcount} records from EXPIRED to expired")
        
        result = await db.execute(text("UPDATE document_approvals SET status = 'auto_approved' WHERE status = 'AUTO_APPROVED'"))
        print(f"✅ Updated {result.rowcount} records from AUTO_APPROVED to auto_approved")
        
        await db.commit()
        
        # Verify the fix
        result = await db.execute(text("SELECT DISTINCT status FROM document_approvals"))
        statuses = result.fetchall()
        print(f"📊 All statuses after fix: {[s[0] for s in statuses]}")
        break

if __name__ == "__main__":
    asyncio.run(fix_enum_values())
