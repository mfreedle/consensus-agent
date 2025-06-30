#!/usr/bin/env python3
"""
Create a test user with known credentials
"""
import asyncio
import sqlite3

from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Create a test user with known credentials"""
    conn = sqlite3.connect('backend/agent_mark.db')
    cursor = conn.cursor()
    
    # Hash password
    password_hash = pwd_context.hash("testpass123")
    
    # Delete existing testuser2 if exists
    cursor.execute("DELETE FROM users WHERE username = ?", ("testuser2",))
    
    # Create new user
    cursor.execute("""
        INSERT INTO users (username, password_hash, is_active) 
        VALUES (?, ?, ?)
    """, ("testuser2", password_hash, True))
    
    conn.commit()
    conn.close()
    print("✅ Created testuser2 with password: testpass123")

if __name__ == "__main__":
    create_test_user()
