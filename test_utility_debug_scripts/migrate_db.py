#!/usr/bin/env python3
"""
Database migration script to add missing columns to approval_templates table.
"""

import asyncio
import sqlite3
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def migrate_database():
    """Add missing columns to approval_templates table."""
    
    db_path = backend_dir / "agent_mark.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if approval_templates table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='approval_templates'")
        if not cursor.fetchone():
            print("❓ approval_templates table doesn't exist - skipping migration")
            return
        
        # Check current columns
        cursor.execute("PRAGMA table_info(approval_templates)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current approval_templates columns: {columns}")
        
        # Drop and recreate the approval_templates table with correct schema
        print("🔄 Dropping and recreating approval_templates table...")
        cursor.execute("DROP TABLE IF EXISTS approval_templates")
        
        cursor.execute("""
            CREATE TABLE approval_templates (
                id INTEGER NOT NULL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                change_types JSON NOT NULL,
                file_patterns JSON,
                content_patterns JSON,
                max_confidence_required FLOAT DEFAULT 0.8,
                max_change_size INTEGER,
                require_ai_reasoning BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT (datetime('now')),
                updated_at DATETIME DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users (id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_user_active ON approval_templates (user_id, is_active)")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    print("🔧 Running database migration...")
    print("=" * 50)
    
    if migrate_database():
        print("🎉 Migration complete!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)
