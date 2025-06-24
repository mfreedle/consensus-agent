#!/usr/bin/env python3
"""
Test script for Agent Mark backend
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def test_database():
    """Test database connection and models"""
    print("🔍 Testing database connection...")
    
    try:
        from app.database.connection import AsyncSessionLocal, engine
        from app.models.user import User
        from sqlalchemy import text

        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Test session
        async with AsyncSessionLocal() as session:
            print("✅ Database session created successfully")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

async def test_llm_orchestrator():
    """Test LLM orchestrator without API calls"""
    print("\n🔍 Testing LLM orchestrator initialization...")
    
    try:
        from app.llm.consensus import LLMOrchestrator, LLMResponse
        
        orchestrator = LLMOrchestrator()
        print("✅ LLM orchestrator initialized")
        
        # Test LLMResponse model
        test_response = LLMResponse(
            content="Test response",
            confidence=0.8,
            reasoning="Test reasoning",
            model="test-model",
            provider="test"
        )
        print("✅ LLMResponse model working")
        
    except Exception as e:
        print(f"❌ LLM orchestrator test failed: {e}")
        return False
    
    return True

async def test_auth_utils():
    """Test authentication utilities"""
    print("\n🔍 Testing authentication utilities...")
    
    try:
        from app.auth.utils import (create_access_token, get_password_hash,
                                    verify_password)

        # Test password hashing
        password = "test123"
        hashed = get_password_hash(password)
        
        if verify_password(password, hashed):
            print("✅ Password hashing and verification working")
        else:
            print("❌ Password verification failed")
            return False
        
        # Test JWT token creation
        token = create_access_token({"sub": "testuser"})
        if token and isinstance(token, str):
            print("✅ JWT token creation working")
        else:
            print("❌ JWT token creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication utilities test failed: {e}")
        return False
    
    return True

async def test_schemas():
    """Test Pydantic schemas"""
    print("\n🔍 Testing Pydantic schemas...")
    
    try:
        from app.schemas.chat import ChatRequest, MessageResponse
        from app.schemas.user import Token, UserCreate, UserResponse

        # Test user schemas
        user_create = UserCreate(username="testuser", password="test123")
        print("✅ User schemas working")
        
        # Test chat schemas  
        chat_request = ChatRequest(message="Hello", use_consensus=True)
        print("✅ Chat schemas working")
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from app.config import settings
        
        print(f"✅ Config loaded - Environment: {settings.app_env}")
        print(f"✅ Database URL configured: {'Yes' if settings.database_url else 'No'}")
        print(f"✅ OpenAI API key configured: {'Yes' if settings.openai_api_key else 'No'}")
        print(f"✅ Grok API key configured: {'Yes' if settings.grok_api_key else 'No'}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

async def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🔍 Testing FastAPI app...")
    
    try:
        from app.main import app
        
        print("✅ FastAPI app created successfully")
        print(f"✅ App title: {app.title}")
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/auth", "/chat", "/models", "/files", "/google"]
        
        for expected in expected_routes:
            found = any(expected in route for route in routes)
            if found:
                print(f"✅ Route prefix '{expected}' found")
            else:
                print(f"⚠️  Route prefix '{expected}' not found")
        
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Agent Mark Backend Tests\n")
    
    tests = [
        ("Configuration", test_config()),
        ("Schemas", test_schemas()),
        ("Authentication", test_auth_utils()),
        ("Database", test_database()),
        ("LLM Orchestrator", test_llm_orchestrator()),
        ("FastAPI App", test_fastapi_app()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*50)
    print(f"Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Backend is ready for testing.")
        print("\n📋 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI and Grok API keys to .env")
        print("3. Run: python setup.py")
        print("4. Run: python dev.py")
        print("5. Visit: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
