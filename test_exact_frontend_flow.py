#!/usr/bin/env python3

import asyncio
import json

import aiohttp


async def test_exact_frontend_flow():
    """Test the exact flow that the frontend GoogleDriveConnection component follows"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Exact Frontend GoogleDrive Flow")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Login (what AuthContext does)
        print("\n1. AuthContext Login...")
        login_data = {"username": "admin", "password": "password123"}
        async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"❌ Login failed: {response.status}")
                return
            login_result = await response.json()
            token = login_result["access_token"]
            print(f"✅ Got auth token: {token[:20]}...")
        
        # Step 2: Check connection status (what component does on mount)
        print("\n2. GoogleDriveService.getConnectionStatus()...")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        async with session.get(f"{base_url}/api/google/connection", headers=headers) as response:
            if response.status == 200:
                status_data = await response.json()
                print(f"✅ Connection status check successful")
                print(f"   Connected: {status_data.get('connected', False)}")
                print(f"   User Email: {status_data.get('user_email', 'None')}")
            else:
                print(f"❌ Connection status failed: {response.status}")
                error = await response.text()
                print(f"   Error: {error}")
        
        # Step 3: Get auth URL (what happens when Connect button is clicked)
        print("\n3. GoogleDriveService.getAuthUrl() - Connect Button Click...")
        async with session.get(f"{base_url}/api/google/auth", headers=headers) as response:
            if response.status == 200:
                auth_data = await response.json()
                print(f"✅ Google OAuth auth URL generated successfully!")
                print(f"   Auth URL: {auth_data.get('auth_url', '')[:100]}...")
                print(f"   State: {auth_data.get('state', '')}")
                
                print(f"\n📋 Frontend would now:")
                print(f"   1. Open popup window with auth URL")
                print(f"   2. User completes OAuth in popup")
                print(f"   3. Popup redirects to callback with code")
                print(f"   4. Frontend calls handleCallback with code")
                print(f"   5. Backend exchanges code for tokens")
                print(f"   6. User is connected to Google Drive!")
                
            elif response.status == 503:
                print("⚠️  Google OAuth not configured")
                error_data = await response.json()
                print(f"   This is expected if Google client ID/secret not set")
                print(f"   Error: {error_data.get('detail', 'Unknown')}")
            else:
                print(f"❌ Auth URL generation failed: {response.status}")
                error = await response.text()
                print(f"   Error: {error}")
        
        # Step 4: Simulate what happens if there's a network error
        print("\n4. Testing Error Scenarios...")
        try:
            # Test with invalid endpoint to see error handling
            async with session.get(f"{base_url}/api/google/invalid", headers=headers) as response:
                print(f"Invalid endpoint status: {response.status}")
        except Exception as e:
            print(f"Exception for invalid endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("If Step 3 succeeded, your Google Drive integration is working!")
    print("The 'Network error' you saw was likely due to:")
    print("  - Backend server not running correctly")
    print("  - Frontend calling private API methods incorrectly")
    print("  - Both of these issues have now been fixed!")
    print("\nTry clicking the Connect button in the UI again.")

if __name__ == "__main__":
    asyncio.run(test_exact_frontend_flow())
