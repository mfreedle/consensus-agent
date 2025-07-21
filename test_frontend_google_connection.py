#!/usr/bin/env python3

import asyncio
import json

import aiohttp


async def test_frontend_google_connection():
    """Test the Google Drive connection from frontend perspective"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Login to get auth token
        login_data = {
            "username": "admin",
            "password": "password123"
        }
        
        print("🔐 Logging in...")
        async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"❌ Login failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            login_result = await response.json()
            token = login_result["access_token"]
            print(f"✅ Login successful, got token: {token[:20]}...")
        
        # Step 2: Test Google OAuth getAuthUrl endpoint
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n🔍 Testing Google OAuth getAuthUrl endpoint...")
        async with session.get(f"{base_url}/api/google/auth", headers=headers) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                auth_data = await response.json()
                print("✅ Google OAuth getAuthUrl successful!")
                print(f"Auth URL: {auth_data.get('auth_url', 'N/A')[:100]}...")
                print(f"State: {auth_data.get('state', 'N/A')}")
                
                # Simulate what frontend would do
                print("\n📋 Frontend simulation:")
                print("1. Frontend would call googleDriveService.getAuthUrl(token)")
                print("2. This makes request to /api/google/auth")
                print("3. Backend returns auth URL and state")
                print("4. Frontend opens popup with auth URL")
                
            elif response.status == 503:
                print("⚠️  Google OAuth not configured (expected in some environments)")
                error_data = await response.json()
                print(f"Error: {error_data.get('detail', 'Unknown error')}")
                
            else:
                print(f"❌ Google OAuth getAuthUrl failed: {response.status}")
                try:
                    error_data = await response.json()
                    print(f"Error: {error_data}")
                except:
                    text = await response.text()
                    print(f"Error text: {text}")
        
        # Step 3: Test other Google endpoints
        print("\n🔍 Testing Google connection status endpoint...")
        async with session.get(f"{base_url}/api/google/connection", headers=headers) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                connection_data = await response.json()
                print(f"✅ Connection status: {connection_data}")
            else:
                print(f"⚠️  Connection status failed: {response.status}")
                try:
                    error_data = await response.json()
                    print(f"Error: {error_data}")
                except:
                    text = await response.text()
                    print(f"Error text: {text}")

if __name__ == "__main__":
    asyncio.run(test_frontend_google_connection())
