#!/usr/bin/env python3
"""
Railway deployment verification script
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def verify_imports():
    """Verify that all required imports work correctly"""
    try:
        from app.main import app
        print("✓ Successfully imported main app")
        
        from app.config import settings
        print("✓ Successfully imported settings")
        
        from app.database.connection import engine
        print("✓ Successfully imported database connection")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_imports()
    sys.exit(0 if success else 1)
