#!/usr/bin/env python3
"""
Debug script to test enum handling
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.document_approval import ApprovalStatus as ModelApprovalStatus
from app.schemas.document_approval import DocumentApprovalResponse
from pydantic import ValidationError

print("🔍 Testing enum handling...")

# Test 1: Check enum values
print("\n1. Model enum values:")
for status in ModelApprovalStatus:
    print(f"   {status.name} = '{status.value}'")

# Test 2: Test creating Pydantic model with different values
print("\n2. Testing Pydantic validation:")

test_data = {
    "id": 1,
    "file_id": 1,
    "chat_session_id": None,
    "title": "Test",
    "description": "Test desc",
    "change_type": "content_edit",  # This might also cause issues
    "original_content": "old",
    "proposed_content": "new",
    "change_location": None,
    "change_metadata": None,
    "ai_reasoning": None,
    "confidence_score": None,
    "approved_at": None,
    "approved_by_user": False,
    "expires_at": "2025-12-31T23:59:59",
    "version_before": None,
    "version_after": None,
    "is_applied": False,
    "applied_at": None,
    "application_error": None,
    "created_at": "2025-06-28T12:00:00",
    "updated_at": "2025-06-28T12:00:00"
}

# Test with lowercase value (what's in database)
print("\n   Testing with 'pending' (lowercase):")
try:
    test_data["status"] = "pending"
    response = DocumentApprovalResponse(**test_data)
    print(f"   ✅ Success: {response.status}")
except ValidationError as e:
    print(f"   ❌ Failed: {e}")

print("\n   Testing with ModelApprovalStatus.PENDING:")
try:
    test_data["status"] = ModelApprovalStatus.PENDING
    response = DocumentApprovalResponse(**test_data)
    print(f"   ✅ Success: {response.status}")
except ValidationError as e:
    print(f"   ❌ Failed: {e}")

print("\n   Testing with 'PENDING' (uppercase):")
try:
    test_data["status"] = "PENDING"
    response = DocumentApprovalResponse(**test_data)
    print(f"   ✅ Success: {response.status}")
except ValidationError as e:
    print(f"   ❌ Failed: {e}")

print("\n   Testing with 'approved' (lowercase):")
try:
    test_data["status"] = "approved"
    response = DocumentApprovalResponse(**test_data)
    print(f"   ✅ Success: {response.status}")
except ValidationError as e:
    print(f"   ❌ Failed: {e}")
