#!/usr/bin/env python3
"""
Check document_versions table schema
"""
import os
import sqlite3
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Checking document_versions table schema...")

# Connect to database
db_path = "agent_mark.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(document_versions)")
columns = cursor.fetchall()

print(f"\n📋 Columns in document_versions table:")
for col in columns:
    print(f"   {col[1]} ({col[2]}) - Nullable: {not col[3]} - Default: {col[4]}")

print("\n🔍 Sample data:")
cursor.execute("SELECT * FROM document_versions LIMIT 1")
sample = cursor.fetchone()
if sample:
    print(f"   Sample row: {sample}")
else:
    print("   No data found")

conn.close()
