#!/usr/bin/env python3
"""
Test the actual FastAPI endpoint
"""

import os
import sys

from fastapi.testclient import TestClient

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import fastapi_app


def test_models_endpoint_authenticated():
    """Test the /api/models endpoint with authentication"""
    client = TestClient(fastapi_app)
    
    # First, let's try to create a test user and get a token
    print("1. Testing models endpoint without auth:")
    response = client.get("/api/models")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}...")
    
    # Try to login to get a token
    print("\n2. Trying to login:")
    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin"  # Default admin password
    })
    print(f"   Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        print(f"   Token received: {token_data.get('access_token', 'N/A')[:50]}...")
        
        # Try the models endpoint with auth
        print("\n3. Testing models endpoint with auth:")
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client.get("/api/models", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response type: {type(data)}")
            print(f"   Is list: {isinstance(data, list)}")
            if isinstance(data, list):
                print(f"   Length: {len(data)}")
                if len(data) > 0:
                    print(f"   First item: {data[0]}")
            else:
                print(f"   Response keys: {list(data.keys()) if hasattr(data, 'keys') else 'N/A'}")
                print(f"   Raw response: {response.text[:300]}...")
        else:
            print(f"   Error response: {response.text}")
    else:
        print(f"   Login failed: {login_response.text}")

if __name__ == "__main__":
    test_models_endpoint_authenticated()
