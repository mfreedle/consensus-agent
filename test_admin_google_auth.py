#!/usr/bin/env python3
"""
Simple test script for Google OAuth authentication
"""

import asyncio
import json

import aiohttp

BASE_URL = "http://localhost:8000"

async def test_admin_auth():
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing admin authentication...")
        
        # Test admin login with correct credentials
        print("\n1. Testing admin login with password123...")
        admin_data = {
            "username": "admin",
            "password": "password123"
        }
        
        token = None
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
                    print("   ✅ Got admin access token!")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test Google debug endpoint with authentication
        if token:
            print("\n2. Testing Google debug endpoint with authentication...")
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
                        print("   ✅ Google OAuth configuration retrieved!")
                        
                        # Check for required OAuth settings
                        if result.get("google_client_id_set"):
                            print("   ✅ Google Client ID is configured")
                        else:
                            print("   ❌ Google Client ID is NOT configured")
                            
                        if result.get("google_client_secret_set"):
                            print("   ✅ Google Client Secret is configured")
                        else:
                            print("   ❌ Google Client Secret is NOT configured")
                            
                        print(f"   App Environment: {result.get('app_env')}")
                        print(f"   Redirect URI: {result.get('google_redirect_uri_resolved')}")
                        
            except Exception as e:
                print(f"   Error: {e}")
        
        # Test Google OAuth URL generation
        if token:
            print("\n3. Testing Google OAuth URL generation...")
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
                        print("   ✅ Google OAuth URL generated successfully!")
                        if "auth_url" in result:
                            print(f"   🔗 Auth URL: {result['auth_url'][:100]}...")
                    else:
                        print("   ❌ Failed to generate Google OAuth URL")
                        if "detail" in result:
                            print(f"   Error details: {result['detail']}")
                        
            except Exception as e:
                print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_admin_auth())
