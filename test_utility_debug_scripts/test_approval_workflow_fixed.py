#!/usr/bin/env python3
"""
Test script for the Document Approval Workflow
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_auth_headers():
    """Get authentication headers"""
    # Login first
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "password123"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    else:
        raise Exception(f"Login failed: {login_response.status_code}")

def test_approval_workflow():
    """Test the complete approval workflow"""
    
    print("🔄 Testing Document Approval Workflow...")
    print("=" * 50)
    
    # Get auth headers
    try:
        headers = get_auth_headers()
        print("✅ Authentication successful!")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False
    
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
    
    # Step 1: Create approval request
    print("\n1. Creating approval request...")
    try:
        response = requests.post(
            f"{BASE_URL}/files/approvals",
            json=test_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            approval = response.json()
            approval_id = approval["id"]
            print(f"✅ Approval created with ID: {approval_id}")
            print(f"   Status: {approval['status']}")
            print(f"   Title: {approval['title']}")
        else:
            print(f"❌ Failed to create approval: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception creating approval: {e}")
        return False
    
    # Step 2: Get pending approvals
    print("\n2. Getting pending approvals...")
    try:
        response = requests.get(f"{BASE_URL}/files/approvals/pending", headers=headers)
        
        if response.status_code == 200:
            approvals = response.json()
            print(f"✅ Found {len(approvals)} pending approvals")
            for approval in approvals[:3]:  # Show first 3
                print(f"   - {approval['title']} (ID: {approval['id']})")
        else:
            print(f"❌ Failed to get pending approvals: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception getting pending approvals: {e}")
    
    # Step 3: Get approval diff
    print(f"\n3. Getting diff for approval {approval_id}...")
    try:
        response = requests.get(f"{BASE_URL}/files/approvals/{approval_id}/diff", headers=headers)
        
        if response.status_code == 200:
            diff = response.json()
            print("✅ Generated diff successfully")
            print(f"   Changes: {len(diff.get('changes', []))} modifications")
            if diff.get('changes'):
                print(f"   Sample change: {diff['changes'][0]}")
        else:
            print(f"❌ Failed to get diff: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception getting diff: {e}")
    
    # Step 4: Approve the request
    print(f"\n4. Approving request {approval_id}...")
    try:
        decision_data = {
            "decision": "approved",
            "reason": "Test approval - changes look good!"
        }
        
        response = requests.post(
            f"{BASE_URL}/files/approvals/{approval_id}/decision",
            json=decision_data,
            headers=headers
        )
        
        if response.status_code == 200:
            approved = response.json()
            print("✅ Approval decision recorded")
            print(f"   New status: {approved['status']}")
            print(f"   Comments: {approved.get('comments', 'None')}")
        else:
            print(f"❌ Failed to approve: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception approving: {e}")
    
    # Step 5: Get approval history
    print("\n5. Getting approval history...")
    try:
        response = requests.get(f"{BASE_URL}/files/approvals/history", headers=headers)
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Retrieved approval history: {len(history)} records")
            for record in history[:3]:  # Show first 3
                print(f"   - {record['title']} ({record['status']}) - {record['created_at'][:10]}")
        else:
            print(f"❌ Failed to get history: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception getting history: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Document Approval Workflow test completed!")
    return True

if __name__ == "__main__":
    test_approval_workflow()
