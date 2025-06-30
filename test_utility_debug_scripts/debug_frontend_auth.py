#!/usr/bin/env python3
"""
Debug script to simulate the exact frontend authentication flow
"""

import time

import requests


def simulate_frontend_flow():
    base_url = "http://localhost:8000"
    
    print("🔍 Simulating Frontend Authentication Flow")
    print("=" * 50)
    
    # Step 1: Login (like the frontend does)
    print("1. Logging in...")
    login_data = {"username": "admin", "password": "password123"}
    login_response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    print(f"✅ Login successful, token: {access_token[:20]}...")
    
    # Step 2: Verify user (like the frontend does)
    print("\n2. Verifying user...")
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = requests.get(f"{base_url}/auth/me", headers=headers)
    
    if me_response.status_code == 200:
        user_data = me_response.json()
        print(f"✅ User verified: {user_data['username']}")
    else:
        print(f"❌ User verification failed: {me_response.status_code}")
        print(f"Response: {me_response.text}")
        return
    
    # Step 3: Make requests to the problematic endpoints (like the frontend does)
    print("\n3. Testing problematic endpoints immediately after login...")
    problematic_endpoints = [
        "/files",
        "/models/providers"
    ]
    
    for endpoint in problematic_endpoints:
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"  {status} {endpoint}: {response.status_code}")
        if response.status_code != 200:
            print(f"    Error: {response.text[:100]}...")
    
    # Step 4: Test after a small delay (in case there's a timing issue)
    print("\n4. Testing after 1 second delay...")
    time.sleep(1)
    
    for endpoint in problematic_endpoints:
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"  {status} {endpoint}: {response.status_code}")
        if response.status_code != 200:
            print(f"    Error: {response.text[:100]}...")

if __name__ == "__main__":
    simulate_frontend_flow()
