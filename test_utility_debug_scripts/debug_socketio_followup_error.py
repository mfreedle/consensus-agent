#!/usr/bin/env python3
"""
Debug script to reproduce and diagnose the Socket.IO follow-up message error.
This script simulates the exact scenario where the first message works but follow-up messages fail.
"""

import asyncio
import logging
import sys

import socketio

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
DEPLOYED_BACKEND_URL = "https://consensus-agent.up.railway.app/"  
TEST_USER_CREDENTIALS = {
    "username": "test_user",
    "password": "test_password"
}

class SocketIOTestClient:
    def __init__(self):
        self.sio = socketio.AsyncClient(logger=True, engineio_logger=True)
        self.received_messages = []
        self.session_id = None
        self.auth_token = None
        
        # Set up event listeners
        self.setup_event_listeners()
    
    def setup_event_listeners(self):
        @self.sio.event
        async def connect():
            logger.info("✅ Connected to Socket.IO server")
        
        @self.sio.event
        async def disconnect():
            logger.info("❌ Disconnected from Socket.IO server")
        
        @self.sio.event
        async def new_message(data):
            logger.info(f"📨 Received new_message: {data}")
            self.received_messages.append(data)
        
        @self.sio.event
        async def session_created(data):
            logger.info(f"🆕 Session created: {data}")
            self.session_id = data.get("session_id")
        
        @self.sio.event
        async def error(data):
            logger.error(f"🚨 Socket.IO error: {data}")
        
        @self.sio.event
        async def connect_error(data):
            logger.error(f"🔌 Connection error: {data}")
    
    async def get_auth_token(self):
        """Get authentication token by logging in"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                login_url = f"{DEPLOYED_BACKEND_URL}api/auth/login"
                
                # Prepare JSON data for login endpoint
                login_data = {
                    'username': TEST_USER_CREDENTIALS['username'],
                    'password': TEST_USER_CREDENTIALS['password']
                }
                
                async with session.post(login_url, json=login_data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.auth_token = token_data.get("access_token")
                        logger.info("✅ Successfully obtained auth token")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to get auth token: {response.status} - {error_text}")
                        return False
                        
        except ImportError:
            logger.error("❌ aiohttp not installed. Install with: pip install aiohttp")
            return False
        except Exception as e:
            logger.error(f"❌ Error getting auth token: {e}")
            return False
    
    async def connect_to_server(self):
        """Connect to the Socket.IO server"""
        try:
            await self.sio.connect(DEPLOYED_BACKEND_URL)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Socket.IO server: {e}")
            return False
    
    async def send_first_message(self):
        """Send the first message (this should work)"""
        if not self.auth_token:
            logger.error("❌ No auth token available")
            return False
        
        message_data = {
            "message": "Hello! This is my first message.",
            "token": self.auth_token,
            "attached_file_ids": [],
            "use_consensus": False,
            "selected_models": ["gpt-4o"]
        }
        
        logger.info("📤 Sending first message...")
        await self.sio.emit('send_message', message_data)
        
        # Wait for response
        await asyncio.sleep(10)  # Give time for response
        
        if self.session_id:
            logger.info(f"✅ First message successful. Session ID: {self.session_id}")
            return True
        else:
            logger.error("❌ First message failed - no session created")
            return False
    
    async def send_followup_message(self):
        """Send a follow-up message (this is where the error occurs)"""
        if not self.auth_token or not self.session_id:
            logger.error("❌ No auth token or session ID available")
            return False
        
        # First, join the existing session room
        await self.sio.emit('join', {"session_id": self.session_id})
        await asyncio.sleep(1)  # Brief pause
        
        message_data = {
            "session_id": self.session_id,
            "message": "This is my follow-up message. Can you help me with something else?",
            "token": self.auth_token,
            "attached_file_ids": [],
            "use_consensus": False,
            "selected_models": ["gpt-4o"]
        }
        
        logger.info("📤 Sending follow-up message...")
        try:
            await self.sio.emit('send_message', message_data)
            
            # Wait for response
            await asyncio.sleep(10)  # Give time for response
            
            logger.info("✅ Follow-up message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending follow-up message: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the server"""
        await self.sio.disconnect()

async def main():
    """Main test function"""
    logger.info("🚀 Starting Socket.IO follow-up message error debugging...")
    
    client = SocketIOTestClient()
    
    try:
        # Step 1: Get authentication token
        logger.info("Step 1: Getting authentication token...")
        if not await client.get_auth_token():
            logger.error("❌ Failed to get auth token. Cannot proceed.")
            return False
        
        # Step 2: Connect to Socket.IO server
        logger.info("Step 2: Connecting to Socket.IO server...")
        if not await client.connect_to_server():
            logger.error("❌ Failed to connect to server. Cannot proceed.")
            return False
        
        # Step 3: Send first message (should work)
        logger.info("Step 3: Sending first message...")
        if not await client.send_first_message():
            logger.error("❌ First message failed. Cannot test follow-up.")
            return False
        
        # Step 4: Send follow-up message (this should reproduce the error)
        logger.info("Step 4: Sending follow-up message...")
        success = await client.send_followup_message()
        
        # Step 5: Analyze results
        logger.info("Step 5: Analyzing results...")
        logger.info(f"📊 Total messages received: {len(client.received_messages)}")
        for i, msg in enumerate(client.received_messages):
            logger.info(f"  Message {i+1}: {msg}")
        
        if success:
            logger.info("✅ Follow-up message test completed successfully")
        else:
            logger.warning("⚠️  Follow-up message test completed with issues")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in main test: {e}")
        return False
    
    finally:
        # Cleanup
        await client.disconnect()

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            logger.info("🎉 Test completed successfully!")
            sys.exit(0)
        else:
            logger.error("💥 Test failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)
