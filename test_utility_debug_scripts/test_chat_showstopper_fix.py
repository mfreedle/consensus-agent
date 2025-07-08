#!/usr/bin/env python3
"""
Test script to validate the chat showstopper fix

This script will test multiple consecutive messages to ensure the fix works.
"""

import asyncio

import aiohttp
import socketio

# Configuration
BASE_URL = "https://consensus-agent.up.railway.app"
API_URL = f"{BASE_URL}/api"
LOGIN_CREDENTIALS = {"username": "admin", "password": "password123"}

class ChatShowstopperTest:
    def __init__(self):
        self.token = None
        self.session_id = None
        self.sio = socketio.AsyncClient()
        self.responses_received = 0
        self.messages_sent = 0
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
            print(f"📨 Message received: {data['role']} - {data['content'][:50]}...")
            if data['role'] == 'assistant':
                self.responses_received += 1
                print(f"🤖 AI Response #{self.responses_received} received!")
            
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
                    self.token = data.get('access_token')
                    if self.token:
                        print("✅ Authenticated successfully")
                        return True
                    else:
                        print("❌ No token found in response")
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

    async def send_message(self, message: str):
        """Send message via Socket.IO"""
        self.messages_sent += 1
        print(f"\n🔄 Sending message #{self.messages_sent}: '{message}'")
        try:
            await self.sio.emit('send_message', {
                'session_id': self.session_id,
                'message': message,
                'token': self.token,
                'attached_file_ids': []
            })
            print("✅ Message sent via Socket.IO")
            return True
        except Exception as e:
            print(f"❌ Socket.IO send failed: {e}")
            return False

    async def test_multiple_messages(self):
        """Test multiple consecutive messages to validate the fix"""
        print("🧪 TESTING CHAT SHOWSTOPPER FIX\n")
        print("Testing multiple consecutive messages to ensure fix works...\n")
        
        # Step 1: Authenticate
        if not await self.authenticate():
            return False
        
        # Step 2: Connect Socket.IO
        if not await self.connect_socket():
            return False
        
        # Step 3: Send multiple messages in sequence
        test_messages = [
            "Hello, this is test message #1",
            "This is test message #2 - does it work?",
            "Test message #3 - checking the fix", 
            "Final test message #4 - should all work now",
            "Message #5 - comprehensive test complete"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{'='*60}")
            print(f"TEST MESSAGE {i}/5")
            print(f"{'='*60}")
            
            success = await self.send_message(message)
            if not success:
                print(f"❌ Failed to send message {i}")
                return False
                
            # Wait for AI response
            print("⏳ Waiting for AI response...")
            initial_responses = self.responses_received
            
            # Wait up to 15 seconds for response
            for _ in range(30):  # 30 * 0.5 = 15 seconds
                await asyncio.sleep(0.5)
                if self.responses_received > initial_responses:
                    break
            else:
                print(f"⚠️  No response received for message {i} within 15 seconds")
                return False
                
            print(f"✅ Message {i} completed successfully!")
        
        # Final results
        print(f"\n{'='*60}")
        print("FINAL RESULTS")
        print(f"{'='*60}")
        print(f"Messages sent: {self.messages_sent}")
        print(f"Responses received: {self.responses_received}")
        
        if self.messages_sent == self.responses_received == len(test_messages):
            print("🎉 SUCCESS: Chat showstopper bug is FIXED!")
            print("✅ All messages sent and received responses correctly")
            return True
        else:
            print("❌ FAILURE: Some messages did not receive responses")
            print("🐛 Chat showstopper bug may still exist")
            return False

    async def cleanup(self):
        """Clean up connections"""
        if self.sio.connected:
            await self.sio.disconnect()

async def main():
    tester = ChatShowstopperTest()
    try:
        success = await tester.test_multiple_messages()
        if success:
            print("\n🚀 Fix validation: PASSED")
        else:
            print("\n💥 Fix validation: FAILED")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
