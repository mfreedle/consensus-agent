import asyncio
import json

import aiohttp


async def test_approval_endpoints():
    """Test the document approval endpoints"""
    
    # First, let's try to get an auth token (using the default user)
    login_data = {
        "username": "admin",
        "password": "password123"
    }
    
    async with aiohttp.ClientSession() as session:
        print("🔐 Testing authentication...")
        
        # Login
        async with session.post(
            "http://localhost:8000/auth/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps(login_data)
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                token = result.get("access_token")
                print(f"✅ Login successful! Token: {token[:20]}...")
                
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test getting pending approvals
                print("\n📋 Testing pending approvals endpoint...")
                async with session.get(
                    "http://localhost:8000/files/approvals/pending",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        approvals = await resp.json()
                        print(f"✅ Pending approvals endpoint working! Found {len(approvals)} approvals")
                    else:
                        print(f"❌ Pending approvals endpoint failed: {resp.status}")
                        text = await resp.text()
                        print(f"Response: {text}")
                
                # Test getting approval history
                print("\n📚 Testing approval history endpoint...")
                async with session.get(
                    "http://localhost:8000/files/approvals/history",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        history = await resp.json()
                        print(f"✅ Approval history endpoint working! Found {len(history)} historical approvals")
                    else:
                        print(f"❌ Approval history endpoint failed: {resp.status}")
                        text = await resp.text()
                        print(f"Response: {text}")
                
                # Test getting files (to see if we have any files to create approvals for)
                print("\n📁 Testing files endpoint...")
                async with session.get(
                    "http://localhost:8000/files",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        files_result = await resp.json()
                        files = files_result.get("files", [])
                        print(f"✅ Files endpoint working! Found {len(files)} files")
                        
                        if files:
                            # Try to create a test approval for the first file
                            test_file = files[0]
                            print(f"\n✨ Creating test approval for file: {test_file.get('filename')}")
                            
                            approval_data = {
                                "file_id": int(test_file["id"]),
                                "title": "Test Document Approval",
                                "description": "This is a test approval to verify the workflow is working",
                                "change_type": "content_edit",
                                "proposed_content": "This is the proposed new content for testing the approval workflow.",
                                "ai_reasoning": "Testing the document approval system functionality",
                                "confidence_score": 85,
                                "expires_in_hours": 24
                            }
                            
                            async with session.post(
                                "http://localhost:8000/files/approvals",
                                headers={**headers, "Content-Type": "application/json"},
                                data=json.dumps(approval_data)
                            ) as resp:
                                if resp.status == 200:
                                    approval = await resp.json()
                                    print(f"✅ Test approval created successfully! ID: {approval['id']}")
                                    
                                    # Test getting the diff for this approval
                                    print(f"\n🔍 Testing diff endpoint for approval {approval['id']}...")
                                    async with session.get(
                                        f"http://localhost:8000/files/approvals/{approval['id']}/diff",
                                        headers=headers
                                    ) as resp:
                                        if resp.status == 200:
                                            diff = await resp.json()
                                            print(f"✅ Diff endpoint working! Change summary: {diff.get('change_summary', 'N/A')}")
                                        else:
                                            print(f"❌ Diff endpoint failed: {resp.status}")
                                else:
                                    print(f"❌ Failed to create test approval: {resp.status}")
                                    text = await resp.text()
                                    print(f"Response: {text}")
                        else:
                            print("ℹ️  No files found to test approval creation")
                    else:
                        print(f"❌ Files endpoint failed: {resp.status}")
                        text = await resp.text()
                        print(f"Response: {text}")
                        
            else:
                print(f"❌ Login failed: {resp.status}")
                text = await resp.text()
                print(f"Response: {text}")

if __name__ == "__main__":
    print("🚀 Testing Document Approval Workflow")
    print("=====================================")
    asyncio.run(test_approval_endpoints())
