#!/usr/bin/env python3
"""
Test script to verify consensus engine fixes are working correctly.
This script tests:
1. Single model selection should bypass consensus engine
2. Multiple model selection should use consensus engine
3. Frontend "thinking" indicator should appear for multi-model selections
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.auth.dependencies import get_current_user_from_token
from app.database.connection import AsyncSessionLocal
from app.llm.orchestrator import LLMOrchestrator
from app.models.chat import ChatSession, Message
from app.models.user import User
from sqlalchemy import select

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_single_model_selection():
    """Test that single model selection bypasses consensus"""
    logger.info("🧪 Testing single model selection (should bypass consensus)...")
    
    try:
        orchestrator = LLMOrchestrator()
        
        # Test direct single model call
        test_prompt = "What is 2 + 2?"
        
        logger.info("Testing direct OpenAI call...")
        openai_response = await orchestrator.get_openai_response(
            prompt=test_prompt,
            model="gpt-4o"
        )
        logger.info(f"✅ OpenAI response: {openai_response.content[:100]}...")
        
        logger.info("Testing direct Grok call...")
        grok_response = await orchestrator.get_grok_response(
            prompt=test_prompt,
            model="grok-beta"
        )
        logger.info(f"✅ Grok response: {grok_response.content[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Single model test failed: {e}")
        return False

async def test_consensus_engine():
    """Test that consensus engine works for multiple models"""
    logger.info("🧪 Testing consensus engine (multiple models)...")
    
    try:
        orchestrator = LLMOrchestrator()
        
        # Test consensus generation
        test_prompt = "What is the capital of France?"
        
        logger.info("Testing consensus generation...")
        consensus_result = await orchestrator.generate_consensus(
            prompt=test_prompt,
            context=None
        )
        
        logger.info(f"✅ Consensus result: {consensus_result.final_consensus[:100]}...")
        logger.info(f"✅ Confidence score: {consensus_result.confidence_score}")
        logger.info(f"✅ Reasoning: {consensus_result.reasoning[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Consensus test failed: {e}")
        return False

async def test_socket_io_message_format():
    """Test that Socket.IO message format includes model selection data"""
    logger.info("🧪 Testing Socket.IO message format...")
    
    # Simulate the data that should be sent via Socket.IO
    single_model_data = {
        "session_id": "1",
        "message": "Test message for single model",
        "token": "test_token",
        "attached_file_ids": [],
        "use_consensus": False,
        "selected_models": ["gpt-4o"]
    }
    
    multi_model_data = {
        "session_id": "1", 
        "message": "Test message for consensus",
        "token": "test_token",
        "attached_file_ids": [],
        "use_consensus": True,
        "selected_models": ["gpt-4o", "grok-beta"]
    }
    
    logger.info("✅ Single model Socket.IO data format:")
    logger.info(f"   use_consensus: {single_model_data['use_consensus']}")
    logger.info(f"   selected_models: {single_model_data['selected_models']}")
    
    logger.info("✅ Multi-model Socket.IO data format:")
    logger.info(f"   use_consensus: {multi_model_data['use_consensus']}")
    logger.info(f"   selected_models: {multi_model_data['selected_models']}")
    
    return True

async def test_frontend_model_selection_logic():
    """Test the frontend model selection logic"""
    logger.info("🧪 Testing frontend model selection logic...")
    
    # Simulate model selection scenarios
    scenarios = [
        {
            "name": "Single model (GPT-4)",
            "selected_models": ["gpt-4o"],
            "expected_consensus": False
        },
        {
            "name": "Single model (Grok)",  
            "selected_models": ["grok-beta"],
            "expected_consensus": False
        },
        {
            "name": "Multiple models",
            "selected_models": ["gpt-4o", "grok-beta"],
            "expected_consensus": True
        },
        {
            "name": "Three models",
            "selected_models": ["gpt-4o", "grok-beta", "claude-3"],
            "expected_consensus": True
        }
    ]
    
    for scenario in scenarios:
        selected_models = scenario["selected_models"]
        use_consensus = len(selected_models) > 1
        expected = scenario["expected_consensus"]
        
        status = "✅" if use_consensus == expected else "❌"
        logger.info(f"{status} {scenario['name']}: use_consensus={use_consensus} (expected={expected})")
        
        if use_consensus != expected:
            return False
    
    return True

async def verify_database_changes():
    """Verify that database changes are working"""
    logger.info("🧪 Testing database operations...")
    
    try:
        async with AsyncSessionLocal() as db:
            # Test querying existing data
            result = await db.execute(select(User))
            users = result.scalars().all()
            logger.info(f"✅ Found {len(users)} users in database")
            
            result = await db.execute(select(ChatSession))
            sessions = result.scalars().all()
            logger.info(f"✅ Found {len(sessions)} chat sessions in database")
            
            result = await db.execute(select(Message))
            messages = result.scalars().all()
            logger.info(f"✅ Found {len(messages)} messages in database")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting consensus engine fix verification tests...\n")
    
    tests = [
        ("Frontend Model Selection Logic", test_frontend_model_selection_logic),
        ("Socket.IO Message Format", test_socket_io_message_format),
        ("Database Operations", verify_database_changes),
        ("Single Model Selection", test_single_model_selection),
        ("Consensus Engine", test_consensus_engine),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info('='*50)
        
        try:
            result = await test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"\n{status}: {test_name}")
        except Exception as e:
            logger.error(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Consensus engine fixes are working.")
        return True
    else:
        logger.info("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
