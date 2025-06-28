#!/usr/bin/env python3
"""
Comprehensive test script for LLM integration in Consensus Agent.

This script tests:
1. Authentication
2. Single model responses (OpenAI, Grok)
3. Multi-model consensus 
4. Chat session management
5. Error handling
"""

import json
import time
from typing import Any, Dict

import requests


class ConsensusAgentTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session_id = None
        
    def login(self, username: str = "admin", password: str = "password123") -> bool:
        """Test user authentication"""
        print("🔐 Testing authentication...")
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                print(f"✅ Login successful! Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_single_model_chat(self, model: str = "gpt-4o-mini", 
                              message: str = "Explain quantum computing in simple terms") -> bool:
        """Test single model chat functionality"""
        print(f"\n🤖 Testing {model} chat...")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/message",
                json={
                    "message": message,
                    "use_consensus": False,
                    "selected_models": [model]
                },
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["message"]["content"]
                self.session_id = data["session"]["id"]
                
                print(f"✅ {model} response received!")
                print(f"📝 Response preview: {content[:150]}...")
                print(f"📊 Session ID: {self.session_id}")
                return True
            else:
                print(f"❌ {model} chat failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ {model} chat error: {e}")
            return False
    
    def test_consensus_chat(self, message: str = "What are the potential risks and benefits of AGI?") -> bool:
        """Test multi-model consensus functionality"""
        print(f"\n🧠 Testing consensus chat...")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/message",
                json={
                    "message": message,
                    "use_consensus": True,
                    "session_id": self.session_id
                },
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                message_data = data["message"]
                consensus_data = message_data.get("consensus_data")
                
                print(f"✅ Consensus response received!")
                print(f"📝 Final consensus: {message_data['content'][:200]}...")
                
                if consensus_data:
                    print(f"\n📊 Consensus Analysis:")
                    print(f"   • Confidence Score: {consensus_data['confidence_score']}")
                    print(f"   • OpenAI Model: {consensus_data['openai_response']['model']}")
                    print(f"   • OpenAI Confidence: {consensus_data['openai_response']['confidence']}")
                    print(f"   • Grok Model: {consensus_data['grok_response']['model']}")
                    print(f"   • Grok Confidence: {consensus_data['grok_response']['confidence']}")
                    print(f"   • Reasoning: {consensus_data['reasoning'][:150]}...")
                    
                    if consensus_data['debate_points']:
                        print(f"   • Debate Points: {len(consensus_data['debate_points'])} identified")
                        for i, point in enumerate(consensus_data['debate_points'][:3], 1):
                            print(f"     {i}. {point}")
                
                return True
            else:
                print(f"❌ Consensus chat failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Consensus chat error: {e}")
            return False
    
    def test_grok_chat(self, message: str = "What makes Grok unique compared to other AI models?") -> bool:
        """Test Grok model specifically"""
        return self.test_single_model_chat("grok-2", message)
    
    def test_chat_sessions(self) -> bool:
        """Test chat session management"""
        print(f"\n📚 Testing chat session management...")
        
        try:
            # Get all sessions
            response = requests.get(
                f"{self.base_url}/chat/sessions",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                sessions = response.json()
                print(f"✅ Found {len(sessions)} chat sessions")
                
                if sessions:
                    # Get messages for the first session
                    session_id = sessions[0]["id"]
                    messages_response = requests.get(
                        f"{self.base_url}/chat/sessions/{session_id}/messages",
                        headers=self.get_headers()
                    )
                    
                    if messages_response.status_code == 200:
                        messages = messages_response.json()
                        print(f"✅ Session {session_id} has {len(messages)} messages")
                        return True
                    else:
                        print(f"❌ Failed to get messages: {messages_response.status_code}")
                        return False
                else:
                    print("ℹ️ No sessions found (expected for new user)")
                    return True
            else:
                print(f"❌ Failed to get sessions: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Session management error: {e}")
            return False
    
    def test_available_models(self) -> bool:
        """Test available models endpoint"""
        print(f"\n🔍 Testing available models...")
        
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Found {len(models)} available models:")
                for model in models:
                    name = model.get('display_name', model.get('name', 'Unknown'))
                    provider = model.get('provider', 'unknown')
                    description = model.get('description', 'No description')
                    status = "🟢 Active" if model.get('is_active', False) else "🔴 Inactive"
                    print(f"   • {name} ({provider}) - {status}: {description}")
                return True
            else:
                print(f"❌ Failed to get models: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Models endpoint error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🚀 Starting Consensus Agent LLM Integration Tests")
        print("=" * 60)
        
        results = {}
        
        # Test authentication
        results["login"] = self.login()
        if not results["login"]:
            print("❌ Authentication failed - stopping tests")
            return results
        
        # Test models endpoint
        results["models"] = self.test_available_models()
        
        # Test single model chats
        results["openai_chat"] = self.test_single_model_chat("gpt-4o-mini")
        results["grok_chat"] = self.test_grok_chat()
        
        # Test consensus
        results["consensus_chat"] = self.test_consensus_chat()
        
        # Test session management
        results["sessions"] = self.test_chat_sessions()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"{test_name.upper():<20} {status}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! LLM integration is working perfectly!")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
        
        return results

def main():
    """Main test function"""
    tester = ConsensusAgentTester()
    results = tester.run_all_tests()
    
    # Return non-zero exit code if any tests failed
    if not all(results.values()):
        exit(1)

if __name__ == "__main__":
    main()
