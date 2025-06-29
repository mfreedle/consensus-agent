import asyncio
import json

import aiohttp


async def test_simple_approval():
    """Test a simple approval workflow"""
    
    login_data = {
        "username": "admin", 
        "password": "password123"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login
        async with session.post(
            "http://localhost:8000/auth/login",
            headers={"Content-Type": "application/json"},
            data=json.dumps(login_data)
        ) as resp:
            result = await resp.json()
            token = result.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            print("✅ Logged in successfully")
            
            # First, let's upload a simple text file
            print("📁 Uploading test file...")
            
            form_data = aiohttp.FormData()
            form_data.add_field('file', 
                              'This is a test document.\nLine 2 of the document.\nLine 3 with some content.',
                              filename='test_document.txt',
                              content_type='text/plain')
            
            async with session.post(
                "http://localhost:8000/files/upload",
                headers={"Authorization": f"Bearer {token}"},
                data=form_data
            ) as resp:
                if resp.status == 200:
                    file_result = await resp.json()
                    file_id = file_result["id"]
                    print(f"✅ File uploaded successfully! ID: {file_id}")
                    
                    # Now create a simple approval
                    print("✨ Creating approval request...")
                    
                    approval_data = {
                        "file_id": file_id,
                        "title": "Simple Test Approval",
                        "description": "Testing the approval workflow",
                        "change_type": "content_edit",
                        "original_content": "This is a test document.\nLine 2 of the document.\nLine 3 with some content.",
                        "proposed_content": "This is a MODIFIED test document.\nLine 2 of the document has been updated.\nLine 3 with some NEW content.",
                        "ai_reasoning": "Updated content for testing purposes",
                        "confidence_score": 90
                    }
                    
                    async with session.post(
                        "http://localhost:8000/files/approvals",
                        headers={**headers, "Content-Type": "application/json"},
                        data=json.dumps(approval_data)
                    ) as resp:
                        if resp.status == 200:
                            approval = await resp.json()
                            print(f"✅ Approval created! ID: {approval['id']}")
                            
                            # Test getting the diff
                            async with session.get(
                                f"http://localhost:8000/files/approvals/{approval['id']}/diff",
                                headers=headers
                            ) as resp:
                                if resp.status == 200:
                                    diff = await resp.json()
                                    print(f"✅ Diff generated: {diff['change_summary']}")
                                    print(f"   Lines added: {diff['lines_added']}")
                                    print(f"   Lines removed: {diff['lines_removed']}")
                                    print(f"   Lines modified: {diff['lines_modified']}")
                                    
                                    # Test approving the change
                                    print("✅ Approving the change...")
                                    async with session.post(
                                        f"http://localhost:8000/files/approvals/{approval['id']}/decision",
                                        headers={**headers, "Content-Type": "application/json"},
                                        data=json.dumps({"decision": "approved"})
                                    ) as resp:
                                        if resp.status == 200:
                                            approved = await resp.json()
                                            print(f"✅ Change approved! Status: {approved['status']}")
                                            print(f"   Applied: {approved['is_applied']}")
                                        else:
                                            print(f"❌ Failed to approve: {resp.status}")
                                            print(await resp.text())
                                else:
                                    print(f"❌ Failed to get diff: {resp.status}")
                                    print(await resp.text())
                        else:
                            print(f"❌ Failed to create approval: {resp.status}")
                            error_text = await resp.text()
                            print(f"Error: {error_text}")
                else:
                    print(f"❌ Failed to upload file: {resp.status}")
                    print(await resp.text())

if __name__ == "__main__":
    print("🧪 Simple Approval Workflow Test")
    print("================================")
    asyncio.run(test_simple_approval())
