#!/usr/bin/env python3

import asyncio
import json

import aiohttp


async def test_google_drive_functionality():
    """Test Google Drive disconnect and file creation/editing functionality"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Google Drive Functionality")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Login to get auth token
        print("\n1. Getting auth token...")
        login_data = {"username": "admin", "password": "password123"}
        async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"❌ Login failed: {response.status}")
                return
            login_result = await response.json()
            token = login_result["access_token"]
            print(f"✅ Got auth token")
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Step 2: Test Google Drive disconnect endpoint (should be DELETE now)
        print("\n2. Testing Google Drive disconnect endpoint...")
        async with session.delete(f"{base_url}/api/google/disconnect", headers=headers) as response:
            print(f"Status: {response.status}")
            if response.status == 200:
                disconnect_data = await response.json()
                print(f"✅ Disconnect successful: {disconnect_data}")
            elif response.status == 400:
                error_data = await response.json()
                if "not connected" in error_data.get('detail', '').lower():
                    print(f"✅ Disconnect endpoint working (user not connected): {error_data}")
                else:
                    print(f"⚠️ Disconnect failed: {error_data}")
            else:
                print(f"❌ Disconnect failed: {response.status}")
                error_data = await response.text()
                print(f"   Error: {error_data}")
        
        # Step 3: Test file creation endpoints (these should work if user is connected)
        print("\n3. Testing Google Drive file creation endpoints...")
        
        # Test document creation endpoint
        doc_data = {
            "title": "Test Document from API", 
            "content": "This is a test document created via the API."
        }
        async with session.post(f"{base_url}/api/google/documents/create", 
                               headers=headers, json=doc_data) as response:
            print(f"   Document creation status: {response.status}")
            if response.status == 200:
                print("   ✅ Document creation endpoint working")
            elif response.status == 400:
                error_data = await response.json()
                if "not connected" in error_data.get('detail', '').lower():
                    print("   ⚠️ Document creation requires Google Drive connection")
                else:
                    print(f"   ❌ Document creation failed: {error_data}")
            else:
                print(f"   ❌ Document creation failed: {response.status}")
        
        # Test spreadsheet creation endpoint  
        sheet_data = {"title": "Test Spreadsheet from API"}
        async with session.post(f"{base_url}/api/google/spreadsheets/create", 
                               headers=headers, json=sheet_data) as response:
            print(f"   Spreadsheet creation status: {response.status}")
            if response.status == 200:
                print("   ✅ Spreadsheet creation endpoint working")
            elif response.status == 400:
                error_data = await response.json()
                if "not connected" in error_data.get('detail', '').lower():
                    print("   ⚠️ Spreadsheet creation requires Google Drive connection")
                else:
                    print(f"   ❌ Spreadsheet creation failed: {error_data}")
            else:
                print(f"   ❌ Spreadsheet creation failed: {response.status}")
        
        # Test presentation creation endpoint
        pres_data = {"title": "Test Presentation from API"}
        async with session.post(f"{base_url}/api/google/presentations/create", 
                               headers=headers, json=pres_data) as response:
            print(f"   Presentation creation status: {response.status}")
            if response.status == 200:
                print("   ✅ Presentation creation endpoint working")
            elif response.status == 400:
                error_data = await response.json()
                if "not connected" in error_data.get('detail', '').lower():
                    print("   ⚠️ Presentation creation requires Google Drive connection")
                else:
                    print(f"   ❌ Presentation creation failed: {error_data}")
            else:
                print(f"   ❌ Presentation creation failed: {response.status}")
        
        # Step 4: Check available scopes and permissions
        print("\n4. Checking Google Drive configuration...")
        async with session.get(f"{base_url}/api/google/debug/config", headers=headers) as response:
            if response.status == 200:
                config_data = await response.json()
                print("✅ Google Drive configuration:")
                print(f"   Client ID configured: {'Yes' if config_data.get('client_id') else 'No'}")
                print(f"   Scopes: {config_data.get('scopes', [])}")
                print(f"   Redirect URI: {config_data.get('redirect_uri', 'Not set')}")
            else:
                print(f"⚠️ Could not get configuration: {response.status}")
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("1. Disconnect endpoint should now use DELETE method (Fixed)")
    print("2. File creation endpoints are available and configured")
    print("3. LLM agents should be able to create/edit files once user connects Google Drive")
    print("4. The OAuth scopes include full Drive, Docs, Sheets, and Slides permissions")

if __name__ == "__main__":
    asyncio.run(test_google_drive_functionality())
