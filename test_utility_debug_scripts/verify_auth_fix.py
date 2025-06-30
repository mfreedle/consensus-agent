#!/usr/bin/env python3
"""
Script to verify frontend authentication is working by comparing 
backend direct calls vs frontend token behavior
"""

import time

import requests


def test_authentication_comparison():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Authentication: Backend vs Frontend")
    print("=" * 60)
    
    # Test 1: Direct backend authentication (should work)
    print("1. Testing direct backend authentication...")
    login_data = {"username": "admin", "password": "password123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code == 200:
        backend_token = response.json()["access_token"]
        print("✅ Backend login successful")
        print(f"🔑 Backend token: {backend_token[:30]}...")
        
        # Test protected endpoints with backend token
        headers = {"Authorization": f"Bearer {backend_token}"}
        endpoints = ["/files", "/models/providers", "/auth/me"]
        
        print("\n2. Testing protected endpoints with backend token:")
        for endpoint in endpoints:
            resp = requests.get(f"{base_url}{endpoint}", headers=headers)
            status = "✅" if resp.status_code == 200 else "❌"
            print(f"  {status} {endpoint}: {resp.status_code}")
        
        print(f"\n3. Frontend should now work with tokens like: {backend_token[:30]}...")
        print("   If frontend still shows 403 errors, the issue is frontend token handling.")
        
    else:
        print(f"❌ Backend login failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_authentication_comparison()
