#!/usr/bin/env python3
"""
Test script for Google OAuth functionality
"""

import asyncio
import json
import sys

import aiohttp

BASE_URL = "http://localhost:8000"

async def test_google_oauth():
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing Consensus Agent Google OAuth...")
        
        # Test 1: Try to access Google debug endpoint without auth
        print("\n1. Testing Google debug endpoint without authentication...")
        try:
            async with session.get(f"{BASE_URL}/api/google/debug/config") as resp:
                result = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Try to register/login a test user
        print("\n2. Testing user registration...")
        user_data = {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "testpassword"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            ) as resp:
                result = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Try to login
        print("\n3. Testing user login...")
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        token = None
        try:
            async with session.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as resp:
                result = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                if resp.status == 200 and "access_token" in result:
                    token = result["access_token"]
                    print(f"   ✅ Got access token!")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Try with admin user if test user failed
        if not token:
            print("\n4. Testing admin login...")
            admin_data = {
                "username": "admin",
                "password": "admin"
            }
            
            try:
                async with session.post(
                    f"{BASE_URL}/api/auth/login",
                    json=admin_data,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    result = await resp.json()
                    print(f"   Status: {resp.status}")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                    
                    if resp.status == 200 and "access_token" in result:
                        token = result["access_token"]
                        print(f"   ✅ Got admin access token!")
            except Exception as e:
                print(f"   Error: {e}")
        
        # Test 5: Access Google debug endpoint with authentication
        if token:
            print("\n5. Testing Google debug endpoint with authentication...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            try:
                async with session.get(
                    f"{BASE_URL}/api/google/debug/config",
                    headers=headers
                ) as resp:
                    result = await resp.json()
                    print(f"   Status: {resp.status}")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                    
                    if resp.status == 200:
                        print(f"   ✅ Google OAuth configuration retrieved!")
                        
                        # Check for required OAuth settings
                        if result.get("google_client_id_set"):
                            print(f"   ✅ Google Client ID is configured")
                        else:
                            print(f"   ❌ Google Client ID is NOT configured")
                            
                        if result.get("google_client_secret_set"):
                            print(f"   ✅ Google Client Secret is configured")
                        else:
                            print(f"   ❌ Google Client Secret is NOT configured")
                            
                        print(f"   App Environment: {result.get('app_env')}")
                        print(f"   Redirect URI: {result.get('google_redirect_uri_resolved')}")
                        
            except Exception as e:
                print(f"   Error: {e}")
        
        # Test 6: Try to get Google auth URL
        if token:
            print("\n6. Testing Google OAuth URL generation...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            try:
                async with session.get(
                    f"{BASE_URL}/api/google/auth",
                    headers=headers
                ) as resp:
                    result = await resp.json()
                    print(f"   Status: {resp.status}")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                    
                    if resp.status == 200:
                        print(f"   ✅ Google OAuth URL generated successfully!")
                        if "auth_url" in result:
                            print(f"   🔗 Auth URL: {result['auth_url'][:100]}...")
                    else:
                        print(f"   ❌ Failed to generate Google OAuth URL")
                        if "detail" in result:
                            print(f"   Error details: {result['detail']}")
                        
            except Exception as e:
                print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_google_oauth())
