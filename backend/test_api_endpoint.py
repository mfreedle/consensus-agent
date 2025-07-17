#!/usr/bin/env python3
"""
Test the LLM models API endpoint
"""

import os
import sys

from fastapi.testclient import TestClient

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import fastapi_app


def test_models_endpoint():
    """Test the /api/models endpoint"""
    client = TestClient(fastapi_app)
    
    # This will fail without auth, but let's see the response
    response = client.get("/api/models")
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 401:
        print("\n✅ API requires authentication (as expected)")
        print("💡 The frontend should handle authentication before calling this endpoint")
    elif response.status_code == 200:
        print(f"\n✅ API returned models successfully: {len(response.json())} models")
    else:
        print(f"\n❌ Unexpected response code: {response.status_code}")

if __name__ == "__main__":
    test_models_endpoint()
