#!/usr/bin/env python3
"""
Test to measure timing of Google Drive function calling and identify timeout issues.
"""

import asyncio
import sys
import time

# Add backend to Python path
sys.path.append('./backend')

# Load environment variables
from dotenv import load_dotenv

load_dotenv('./backend/.env')

async def test_timing_and_timeout_issues():
    """Test timing of function calling to identify timeout issues"""
    
    print("⏱️  Testing Google Drive Function Calling Timing")
    print("=" * 55)
    
    try:
        from app.config import settings
        from app.google.service import GoogleDriveService
        from app.llm.google_drive_tools import GoogleDriveTools
        from app.llm.orchestrator import LLMOrchestrator

        # Setup
        llm_orchestrator = LLMOrchestrator()
        google_service = GoogleDriveService(settings)
        google_drive_tools = GoogleDriveTools(google_service)
        llm_orchestrator.set_google_drive_tools(google_drive_tools)
        
        # Mock user without Google Drive token (like in real scenario)
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "test_user"
                self.google_drive_token = None
                self.google_refresh_token = None
        
        user = MockUser()
        
        test_message = "Hello, In my AI Workshop folder there is a file named one_pager_v03.md. Please make a copy of it and put the copy in the main Google Drive folder."
        
        print(f"📝 Testing message: {test_message[:50]}...")
        print(f"👤 User has Google Drive token: {user.google_drive_token is not None}")
        
        # Test with timing
        start_time = time.time()
        print(f"\n⏰ Starting function call at {time.strftime('%H:%M:%S')}")
        
        try:
            response = await llm_orchestrator.get_openai_response_with_tools(
                prompt=test_message,
                user=user,
                model="gpt-4.1",
                context="",
                enable_google_drive=True
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏰ Function call completed at {time.strftime('%H:%M:%S')}")
            print(f"⏱️  Total duration: {duration:.2f} seconds")
            
            print(f"\n📄 Response length: {len(response.content)}")
            print(f"📄 Response content:")
            print("-" * 50)
            print(response.content)
            print("-" * 50)
            
            # Analyze if this would cause timeout
            if duration > 30:
                print(f"\n⚠️  WARNING: Duration ({duration:.2f}s) > 30s - this could cause socket timeouts!")
            elif duration > 20:
                print(f"\n⚠️  CAUTION: Duration ({duration:.2f}s) > 20s - approaching timeout threshold")
            else:
                print(f"\n✅ Duration ({duration:.2f}s) is acceptable")
            
            # Check if the response indicates the real issue
            if "Google Drive not connected" in response.content:
                print(f"\n🎯 ROOT CAUSE IDENTIFIED:")
                print(f"   The user needs to connect their Google Drive account!")
                print(f"   The LLM and function calling are working correctly.")
                return True
            elif "NO_GOOGLE_DRIVE_TOKEN" in response.content:
                print(f"\n🎯 ROOT CAUSE IDENTIFIED:")
                print(f"   Google Drive token is missing - user needs to authenticate!")
                return True
            else:
                print(f"\n🤔 Response doesn't clearly indicate Google Drive connection issue")
                
            return True
            
        except asyncio.TimeoutError:
            end_time = time.time()
            duration = end_time - start_time
            print(f"\n❌ TIMEOUT ERROR after {duration:.2f} seconds")
            print(f"   This explains the socket disconnection!")
            return False
            
        except Exception as api_error:
            end_time = time.time()
            duration = end_time - start_time
            print(f"\n❌ API ERROR after {duration:.2f} seconds: {api_error}")
            return False
        
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        return False

async def test_simple_api_call_timing():
    """Test a simple API call without function calling for comparison"""
    
    print(f"\n🔄 Testing Simple API Call (No Function Calling)")
    print("=" * 55)
    
    try:
        from app.llm.orchestrator import LLMOrchestrator
        
        llm_orchestrator = LLMOrchestrator()
        
        start_time = time.time()
        print(f"⏰ Starting simple API call at {time.strftime('%H:%M:%S')}")
        
        response = await llm_orchestrator.get_openai_response(
            prompt="Just respond with 'Hello, this is a simple test'",
            model="gpt-4.1-mini",
            context=""
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏰ Simple API call completed at {time.strftime('%H:%M:%S')}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📄 Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple API call failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🧪 Google Drive Function Calling Timeout Analysis")
        print("=" * 60)
        
        # Test 1: Function calling with timing
        success1 = await test_timing_and_timeout_issues()
        
        # Test 2: Simple API call for comparison
        success2 = await test_simple_api_call_timing()
        
        print(f"\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        
        if success1 and success2:
            print("✅ Both tests completed successfully")
            print("🔍 Check the timing analysis above to identify the issue")
        elif success1:
            print("✅ Function calling works, but simple API call failed")
            print("🤔 This suggests a configuration issue")
        elif success2:
            print("✅ Simple API call works, but function calling failed")
            print("🎯 This suggests a function calling specific issue")
        else:
            print("❌ Both tests failed - check API configuration")
        
        print(f"\n💡 LIKELY SOLUTION:")
        print(f"   1. User needs to connect Google Drive account in frontend")
        print(f"   2. Check if socket timeout settings need adjustment")
        print(f"   3. Consider adding better error handling for missing tokens")
    
    asyncio.run(main())
