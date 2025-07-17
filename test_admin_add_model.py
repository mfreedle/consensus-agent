#!/usr/bin/env python3
"""
Test script to debug the admin panel "Add Model" functionality
"""
import asyncio
import json
import os
import sys
from datetime import datetime

import httpx

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_add_model_api():
    """Test the add model API endpoint directly"""
    
    print("🔧 Testing Admin Panel Add Model API")
    print("=" * 50)
    
    # First, let's try to get a token (login)
    login_url = "http://localhost:8000/auth/login"
    models_url = "http://localhost:8000/models/admin/models"
    
    login_data = {
        "username": "admin",
        "password": "password123"
    }
    
    try:
        print("1. 🔐 Testing login...")
        async with httpx.AsyncClient() as client:
            # Login
            login_response = await client.post(
                login_url,
                data=login_data,  # Form data for login
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data.get("access_token")
                print(f"✅ Login successful, token received")
                
                # Test adding Grok 4 model
                print("\\n2. 🤖 Testing add Grok 4 model...")
                
                new_model_data = {
                    "model_id": "grok-4-latest",
                    "provider": "grok",
                    "display_name": "Grok 4",
                    "description": "Latest Grok 4 model from xAI",
                    "is_active": True,
                    "supports_streaming": True,
                    "supports_function_calling": True,
                    "supports_vision": False,
                    "context_window": 128000
                }
                
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                add_response = await client.post(
                    models_url,
                    json=new_model_data,
                    headers=headers
                )
                
                print(f"📊 Response Status: {add_response.status_code}")
                print(f"📝 Response Body: {add_response.text}")
                
                if add_response.status_code == 200:
                    result = add_response.json()
                    print("✅ Model added successfully!")
                    print(f"📋 Result: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Failed to add model: {add_response.status_code}")
                    try:
                        error_data = add_response.json()
                        print(f"🚨 Error details: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"🚨 Error text: {add_response.text}")
                
                # Test getting all models to see if it was added
                print("\\n3. 📋 Testing get all models...")
                get_response = await client.get(
                    "http://localhost:8000/models",
                    headers=headers
                )
                
                if get_response.status_code == 200:
                    models = get_response.json()
                    grok_models = [m for m in models if m.get('provider') == 'grok']
                    print(f"✅ Found {len(grok_models)} Grok models:")
                    for model in grok_models:
                        print(f"  - {model.get('id', 'unknown')}: {model.get('display_name', 'unknown')}")
                else:
                    print(f"❌ Failed to get models: {get_response.status_code}")
                
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    print("\\n" + "=" * 50)
    print("🔍 Debugging Notes:")
    print("- Backend server should be running on localhost:8000")
    print("- Admin credentials: admin / password123")
    print("- Check backend logs for additional error details")
    print("- Verify the models are being saved to the JSON file")

if __name__ == "__main__":
    print(f"🕐 Test started at {datetime.now()}")
    asyncio.run(test_add_model_api())
