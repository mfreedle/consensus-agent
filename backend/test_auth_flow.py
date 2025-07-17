#!/usr/bin/env python3
"""
Test the authentication flow for the models API
"""

import os
import sys

from fastapi.testclient import TestClient

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import fastapi_app


def test_auth_flow():
    """Test the complete authentication flow"""
    client = TestClient(fastapi_app)
    
    print("1. Testing models endpoint without auth:")
    response = client.get("/api/models")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.text[:200]}...")
    
    print("\n2. Testing auth endpoint:")
    # Try to get auth endpoint info
    try:
        response = client.get("/auth/me")
        print(f"   /auth/me Status: {response.status_code}")
    except Exception as e:
        print(f"   /auth/me Error: {e}")
    
    print("\n3. Testing login endpoint:")
    try:
        response = client.post("/auth/login", json={"username": "test", "password": "test"})
        print(f"   Login Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Login Error: {e}")
    
    print("\n💡 The frontend needs a valid auth token to access /api/models")
    print("💡 Check browser console for authentication errors")

if __name__ == "__main__":
    test_auth_flow()
