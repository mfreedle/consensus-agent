#!/usr/bin/env python3
"""
Debug script for the chat showstopper bug - "Chat only works on first message"

Root cause analysis:
- First message: Socket.IO works, returns early 
- Second message: Socket.IO fails, HTTP API fallback has issues

This script tests both Socket.IO and HTTP API paths to isolate the problem.
"""

import asyncio

import aiohttp
import socketio

# Configuration
BASE_URL = "https://consensus-agent.up.railway.app"
API_URL = f"{BASE_URL}/api"
LOGIN_CREDENTIALS = {"username": "admin", "password": "password123"}

class ChatDebugger:
    def __init__(self):
        self.token = None
        self.session_id = None
        self.sio = socketio.AsyncClient()
        self.setup_socket_events()
    
    def setup_socket_events(self):
        @self.sio.event
        async def connect():
            print("✅ Socket.IO connected")
        
        @self.sio.event  
        async def disconnect():
            print("❌ Socket.IO disconnected")
            
        @self.sio.on('new_message')
        async def on_new_message(data):
            print(f"📨 Socket.IO message received: {data}")
            
        @self.sio.on('error')
        async def on_error(data):
            print(f"❌ Socket.IO error: {data}")
            
        @self.sio.on('session_created')
        async def on_session_created(data):
            print(f"🆕 Session created: {data}")
            self.session_id = data.get('session_id')

    async def authenticate(self):
        """Get JWT token via HTTP API"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_URL}/auth/login", json=LOGIN_CREDENTIALS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"📋 Auth response: {data}")
                    # Try different possible token keys
                    self.token = data.get('token') or data.get('access_token') or data.get('data', {}).get('token')
                    if self.token:
                        print(f"✅ Authenticated, token: {self.token[:20]}...")
                        return True
                    else:
                        print(f"❌ No token found in response: {data}")
                        return False
                else:
                    error_text = await resp.text()
                    print(f"❌ Auth failed: {resp.status} - {error_text}")
                    return False

    async def connect_socket(self):
        """Connect to Socket.IO"""
        try:
            await self.sio.connect(BASE_URL)
            print("✅ Socket.IO connection established")
            return True
        except Exception as e:
            print(f"❌ Socket.IO connection failed: {e}")
            return False

    async def send_via_socket(self, message: str):
        """Send message via Socket.IO"""
        print(f"\n🔄 Sending via Socket.IO: '{message}'")
        try:
            await self.sio.emit('send_message', {
                'session_id': self.session_id,
                'message': message,
                'token': self.token,
                'attached_file_ids': []
            })
            print("✅ Socket.IO message sent")
            return True
        except Exception as e:
            print(f"❌ Socket.IO send failed: {e}")
            return False

    async def send_via_http(self, message: str):
        """Send message via HTTP API"""
        print(f"\n🔄 Sending via HTTP API: '{message}'")
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'message': message,
            'session_id': self.session_id,
            'use_consensus': False,
            'selected_models': ['gpt-4o'],
            'attached_file_ids': []
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{API_URL}/chat/message", 
                                        headers=headers, 
                                        json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"✅ HTTP API success: {data}")
                        return True
                    else:
                        error_text = await resp.text()
                        print(f"❌ HTTP API failed: {resp.status} - {error_text}")
                        return False
        except Exception as e:
            print(f"❌ HTTP API error: {e}")
            return False

    async def test_chat_flow(self):
        """Test the complete chat flow that reproduces the bug"""
        print("🧪 TESTING CHAT SHOWSTOPPER BUG\n")
        
        # Step 1: Authenticate
        if not await self.authenticate():
            return
        
        # Step 2: Connect Socket.IO
        socket_connected = await self.connect_socket()
        
        # Step 3: Test first message (should work)
        print("\n" + "="*50)
        print("TEST 1: First message (should work)")
        print("="*50)
        
        if socket_connected:
            success1 = await self.send_via_socket("Hello, this is my first message")
            await asyncio.sleep(3)  # Wait for response
        else:
            success1 = await self.send_via_http("Hello, this is my first message")
            
        # Step 4: Test second message (reproduces bug)
        print("\n" + "="*50)
        print("TEST 2: Second message (reproduces bug)")
        print("="*50)
        
        if socket_connected:
            success2 = await self.send_via_socket("This is my second message - does it work?")
            await asyncio.sleep(3)  # Wait for response
        else:
            success2 = await self.send_via_http("This is my second message - does it work?")
        
        # Step 5: Force HTTP fallback test
        print("\n" + "="*50)
        print("TEST 3: Force HTTP API fallback")
        print("="*50)
        success3 = await self.send_via_http("This is an HTTP-only message")
        
        # Summary
        print("\n" + "="*50)
        print("RESULTS SUMMARY")
        print("="*50)
        print(f"First message (Socket.IO): {'✅ SUCCESS' if success1 else '❌ FAILED'}")
        print(f"Second message (Socket.IO): {'✅ SUCCESS' if success2 else '❌ FAILED'}")
        print(f"HTTP fallback: {'✅ SUCCESS' if success3 else '❌ FAILED'}")
        
        if success1 and not success2:
            print("\n🚨 BUG REPRODUCED: Chat works on first message but fails on second!")
        elif success1 and success2 and success3:
            print("\n✅ All tests passed - bug may be fixed or frontend-specific")
        else:
            print("\n❓ Unexpected pattern - need further investigation")

    async def cleanup(self):
        """Clean up connections"""
        if self.sio.connected:
            await self.sio.disconnect()

async def main():
    debugger = ChatDebugger()
    try:
        await debugger.test_chat_flow()
    finally:
        await debugger.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
