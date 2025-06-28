#!/usr/bin/env python3
"""
Test script for the Document Approval Workflow
"""
import asyncio
import json
from datetime import datetime

import aiohttp

BASE_URL = "http://localhost:8000"

async def test_approval_workflow():
    """Test the complete approval workflow"""
    
    # Sample test data
    test_data = {
        "file_id": 1,
        "title": "Sample Document Edit",
        "description": "Testing the approval workflow with a sample document edit",
        "change_type": "content_edit",
        "original_content": "This is the original content of the document.",
        "proposed_content": "This is the revised content of the document with improvements.",
        "ai_reasoning": "The proposed changes improve clarity and readability",
        "confidence_score": 85,
        "expires_in_hours": 24
    }
    
    async with aiohttp.ClientSession() as session:
        print("🔄 Testing Document Approval Workflow...")
        print("=" * 50)
        
        # Test 1: Create a new approval request
        print("\n1. Creating approval request...")
        try:
            async with session.post(
                f"{BASE_URL}/files/approvals",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    approval = await response.json()
                    approval_id = approval["id"]
                    print(f"✅ Created approval #{approval_id}: {approval['title']}")
                    print(f"   Status: {approval['status']}")
                    print(f"   Change Type: {approval['change_type']}")
                else:
                    print(f"❌ Failed to create approval: {response.status}")
                    text = await response.text()
                    print(f"   Error: {text}")
                    return
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return
        
        # Test 2: Get pending approvals
        print("\n2. Fetching pending approvals...")
        try:
            async with session.get(f"{BASE_URL}/files/approvals/pending") as response:
                if response.status == 200:
                    approvals = await response.json()
                    print(f"✅ Found {len(approvals)} pending approval(s)")
                    for approval in approvals:
                        print(f"   - #{approval['id']}: {approval['title']} ({approval['status']})")
                else:
                    print(f"❌ Failed to fetch approvals: {response.status}")
        except Exception as e:
            print(f"❌ Error fetching approvals: {e}")
        
        # Test 3: Get content diff
        print("\n3. Testing content diff...")
        try:
            async with session.get(f"{BASE_URL}/files/approvals/{approval_id}/diff") as response:
                if response.status == 200:
                    diff = await response.json()
                    print(f"✅ Generated diff:")
                    print(f"   Lines added: {diff['lines_added']}")
                    print(f"   Lines removed: {diff['lines_removed']}")
                    print(f"   Lines modified: {diff['lines_modified']}")
                    print(f"   Summary: {diff['change_summary']}")
                else:
                    print(f"❌ Failed to get diff: {response.status}")
        except Exception as e:
            print(f"❌ Error getting diff: {e}")
        
        # Test 4: Approve the request
        print("\n4. Approving the request...")
        try:
            decision_data = {
                "decision": "approved",
                "reason": "Changes look good and improve the content"
            }
            async with session.post(
                f"{BASE_URL}/files/approvals/{approval_id}/decision",
                json=decision_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    approved = await response.json()
                    print(f"✅ Approval processed: {approved['status']}")
                    print(f"   Applied: {approved['is_applied']}")
                    if approved.get('applied_at'):
                        print(f"   Applied at: {approved['applied_at']}")
                else:
                    print(f"❌ Failed to approve: {response.status}")
                    text = await response.text()
                    print(f"   Error: {text}")
        except Exception as e:
            print(f"❌ Error approving: {e}")
        
        # Test 5: Get approval history
        print("\n5. Checking approval history...")
        try:
            async with session.get(f"{BASE_URL}/files/approvals/history") as response:
                if response.status == 200:
                    history = await response.json()
                    print(f"✅ Found {len(history)} approval(s) in history")
                    for approval in history:
                        print(f"   - #{approval['id']}: {approval['title']} ({approval['status']})")
                else:
                    print(f"❌ Failed to fetch history: {response.status}")
        except Exception as e:
            print(f"❌ Error fetching history: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Document Approval Workflow test completed!")

if __name__ == "__main__":
    asyncio.run(test_approval_workflow())
