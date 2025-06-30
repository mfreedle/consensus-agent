#!/usr/bin/env python3
"""
Debug script to test authentication flow
"""

import json

import requests


def test_auth_flow():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Authentication Flow")
    print("=" * 50)
    
    # Test 1: Login
    print("1. Testing login...")
    login_data = {"username": "admin", "password": "password123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Login successful")
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"🔑 Token: {access_token[:20]}...")
        
        # Test 2: Verify token with /auth/me
        print("\n2. Testing token verification...")
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = requests.get(f"{base_url}/auth/me", headers=headers)
        
        if me_response.status_code == 200:
            print("✅ Token verification successful")
            user_data = me_response.json()
            print(f"👤 User: {user_data['username']}")
            
            # Test 3: Test protected endpoints
            print("\n3. Testing protected endpoints...")
            test_endpoints = [
                "/files/",
                "/files/approvals/pending?limit=20",
                "/files/approvals/history?limit=20", 
                "/models/",
                "/models/providers",
                "/google/connection"
            ]
            
            for endpoint in test_endpoints:
                test_response = requests.get(f"{base_url}{endpoint}", headers=headers)
                status = "✅" if test_response.status_code == 200 else "❌"
                print(f"  {status} {endpoint}: {test_response.status_code}")
                
        else:
            print(f"❌ Token verification failed: {me_response.status_code}")
            print(f"Response: {me_response.text}")
            
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_auth_flow()
