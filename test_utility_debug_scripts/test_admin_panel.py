#!/usr/bin/env python3
"""
Quick test script to verify the unified provider/model management backend endpoints
"""

import json

import requests

BASE_URL = "http://localhost:8000"

def test_backend_endpoints():
    """Test the backend endpoints for provider and model management"""
    
    print("🧪 Testing Unified Provider & Model Management Backend Endpoints")
    print("=" * 60)
    
    # Test models endpoint
    print("\n1. Testing GET /models endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ SUCCESS: Retrieved {len(models)} models")
            
            # Group by provider
            providers = {}
            for model in models:
                provider = model.get('provider', 'unknown')
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append(model['display_name'])
            
            for provider, model_names in providers.items():
                print(f"   📊 {provider}: {len(model_names)} models")
                for name in model_names[:3]:  # Show first 3
                    print(f"      - {name}")
                if len(model_names) > 3:
                    print(f"      ... and {len(model_names) - 3} more")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test providers endpoint
    print("\n2. Testing GET /models/providers endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/models/providers")
        if response.status_code == 200:
            providers = response.json()
            print(f"✅ SUCCESS: Retrieved {len(providers)} provider configurations")
            if len(providers) == 0:
                print("   📝 NOTE: No providers configured yet (expected for new installation)")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test health endpoint
    print("\n3. Testing general API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ SUCCESS: API is healthy")
        else:
            print(f"❌ API health check failed: Status {response.status_code}")
    except Exception as e:
        try:
            # Try root endpoint if health doesn't exist
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ SUCCESS: API is responding")
            else:
                print(f"❌ API not responding properly: Status {response.status_code}")
        except Exception as e2:
            print(f"❌ ERROR: Cannot connect to API - {e2}")
    
    print("\n" + "=" * 60)
    print("✨ Test completed! If you see ✅ marks above, the backend is working correctly.")
    print("🌐 Frontend should be accessible at: http://localhost:3000")
    print("🔧 Backend API is at: http://localhost:8000")

if __name__ == "__main__":
    test_backend_endpoints()
