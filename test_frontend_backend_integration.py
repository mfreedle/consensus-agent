#!/usr/bin/env python3

import asyncio
import json

import aiohttp


async def test_frontend_backend_integration():
    """Test frontend to backend Google API integration"""
    
    # Test if frontend can call backend API properly
    base_url = "http://localhost:3000"  # Frontend URL
    api_url = "http://localhost:8000"   # Backend URL
    
    print("🔍 Testing Frontend to Backend Integration")
    print("=" * 50)
    
    # Test 1: Check if frontend serves properly
    print("\n1. Testing Frontend Accessibility...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{base_url}") as response:
                if response.status == 200:
                    print("✅ Frontend is accessible at http://localhost:3000")
                else:
                    print(f"❌ Frontend returned status: {response.status}")
        except Exception as e:
            print(f"❌ Frontend connection failed: {e}")
    
    # Test 2: Check if backend serves properly
    print("\n2. Testing Backend Accessibility...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{api_url}/api/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Backend is healthy: {health_data}")
                else:
                    print(f"❌ Backend health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
    
    # Test 3: Check CORS configuration
    print("\n3. Testing CORS Configuration...")
    async with aiohttp.ClientSession() as session:
        headers = {"Origin": "http://localhost:3000"}
        try:
            async with session.options(f"{api_url}/api/google/auth", headers=headers) as response:
                if response.status in [200, 204]:
                    print("✅ CORS preflight successful")
                    cors_headers = dict(response.headers)
                    if 'access-control-allow-origin' in cors_headers:
                        print(f"✅ CORS Origin allowed: {cors_headers['access-control-allow-origin']}")
                    else:
                        print("⚠️  CORS Origin header not found")
                else:
                    print(f"❌ CORS preflight failed: {response.status}")
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
    
    # Test 4: Simulate frontend API call
    print("\n4. Simulating Frontend API Call...")
    async with aiohttp.ClientSession() as session:
        # First login
        login_data = {"username": "admin", "password": "password123"}
        try:
            async with session.post(f"{api_url}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    login_result = await response.json()
                    token = login_result["access_token"]
                    print(f"✅ Login successful")
                    
                    # Now test Google auth endpoint with token
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Origin": "http://localhost:3000",
                        "Content-Type": "application/json"
                    }
                    
                    async with session.get(f"{api_url}/api/google/auth", headers=headers) as response:
                        if response.status == 200:
                            google_data = await response.json()
                            print("✅ Google OAuth endpoint accessible from frontend!")
                            print(f"   Auth URL generated: {google_data.get('auth_url', '')[:80]}...")
                        elif response.status == 503:
                            print("⚠️  Google OAuth not configured (this is expected)")
                        else:
                            print(f"❌ Google OAuth endpoint failed: {response.status}")
                            error_data = await response.text()
                            print(f"   Error: {error_data}")
                else:
                    print(f"❌ Login failed: {response.status}")
        except Exception as e:
            print(f"❌ API call simulation failed: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("If all tests pass, the frontend should be able to connect to Google Drive.")
    print("If there are still issues, check browser developer tools for specific errors.")

if __name__ == "__main__":
    asyncio.run(test_frontend_backend_integration())
