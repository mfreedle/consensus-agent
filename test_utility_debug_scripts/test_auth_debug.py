#!/usr/bin/env python3
"""
Test script to debug authentication issues
"""
import asyncio
import json

import aiohttp


async def test_auth_flow():
    """Test the authentication flow and provider endpoints"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Try to login
        print("=== Testing Login ===")
        login_data = {
            "username": "admin",  # Assuming there's an admin user
            "password": "admin"   # Assuming default password
        }
        
        # First, let's see what users exist - try a few common combinations
        test_users = [
            {"username": "testuser2", "password": "testpass123"},
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
            {"username": "test", "password": "test"},
            {"username": "user", "password": "user"}
        ]
        
        token = None
        
        for user_data in test_users:
            try:
                async with session.post(f"{base_url}/auth/login", json=user_data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        token = result.get("access_token")
                        print(f"✅ Login successful with {user_data['username']}")
                        print(f"Token: {token[:50]}..." if token else "No token")
                        break
                    else:
                        print(f"❌ Login failed for {user_data['username']}: {resp.status}")
            except Exception as e:
                print(f"❌ Login error for {user_data['username']}: {e}")
        
        if not token:
            print("❌ Could not authenticate with any test credentials")
            # Try to register a user
            print("\n=== Testing Registration ===")
            register_data = {
                "username": "testuser",
                "password": "testpass"
            }
            try:
                async with session.post(f"{base_url}/auth/register", json=register_data) as resp:
                    if resp.status == 200 or resp.status == 201:
                        result = await resp.json()
                        print("✅ Registration successful")
                        # Try to login with new user
                        async with session.post(f"{base_url}/auth/login", json=register_data) as resp2:
                            if resp2.status == 200:
                                result = await resp2.json()
                                token = result.get("access_token")
                                print(f"✅ Login successful with new user")
                            else:
                                print(f"❌ Login failed after registration: {resp2.status}")
                    else:
                        print(f"❌ Registration failed: {resp.status}")
                        resp_text = await resp.text()
                        print(f"Response: {resp_text}")
            except Exception as e:
                print(f"❌ Registration error: {e}")
                return
        
        if not token:
            print("❌ No valid token obtained")
            return
        
        # Test 2: Try to access provider endpoints with token
        print(f"\n=== Testing Provider Endpoints with Token ===")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test GET /models/providers
        try:
            async with session.get(f"{base_url}/models/providers", headers=headers) as resp:
                print(f"GET /models/providers: {resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ Providers retrieved: {len(result)} providers")
                else:
                    resp_text = await resp.text()
                    print(f"❌ Error: {resp_text}")
        except Exception as e:
            print(f"❌ Error accessing providers: {e}")
        
        # Test POST /models/providers (create/update provider)
        provider_data = {
            "provider": "openai",
            "display_name": "OpenAI Test",
            "api_key": "test-key",
            "api_base_url": "https://api.openai.com/v1",
            "is_active": True,
            "max_requests_per_minute": 60,
            "max_tokens_per_request": 4000,
            "auto_sync_models": True
        }
        
        try:
            async with session.post(f"{base_url}/models/providers", 
                                    headers=headers, 
                                    json=provider_data) as resp:
                print(f"POST /models/providers: {resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print("✅ Provider created/updated successfully")
                else:
                    resp_text = await resp.text()
                    print(f"❌ Error: {resp_text}")
        except Exception as e:
            print(f"❌ Error creating provider: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
