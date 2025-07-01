#!/usr/bin/env python3
"""
Test script to verify complete delete functionality (backend + instructions for frontend)
"""
import requests


def test_complete_delete_functionality():
    """Test the complete delete functionality"""
    print("🗑️  Testing Complete Delete Conversation Functionality\n")
    
    # Test backend first
    print("🧪 Testing backend delete functionality...")
    
    # Login to get token
    login_data = {'username': 'admin', 'password': 'password123'}
    login_response = requests.post('http://localhost:8000/auth/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
        
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get sessions before deletion
    sessions_response = requests.get('http://localhost:8000/chat/sessions', headers=headers)
    
    if sessions_response.status_code != 200:
        print(f"❌ Failed to get sessions: {sessions_response.status_code}")
        return False
        
    sessions_before = sessions_response.json()
    print(f"✅ Found {len(sessions_before)} sessions before testing")
    
    if len(sessions_before) == 0:
        print("❌ No sessions available for testing")
        return False
    
    # Find a session to delete (skip the first one, use one from the middle)
    target_session = None
    for session in sessions_before[1:]:  # Skip first session
        if session.get('title') != 'New Chat':
            target_session = session
            break
    
    if not target_session:
        print("❌ No suitable session found for testing")
        return False
    
    session_id = target_session['id']
    session_title = target_session.get('title', 'Untitled')
    
    print(f"🎯 Target session for deletion: ID {session_id}, Title: '{session_title}'")
    
    # Delete the session
    delete_response = requests.delete(
        f'http://localhost:8000/chat/sessions/{session_id}',
        headers=headers
    )
    
    if delete_response.status_code != 200:
        print(f"❌ Delete request failed: {delete_response.status_code}")
        print(f"   Response: {delete_response.text}")
        return False
    
    print("✅ Delete request successful!")
    
    # Verify session is deleted
    sessions_response_after = requests.get('http://localhost:8000/chat/sessions', headers=headers)
    sessions_after = sessions_response_after.json()
    
    print(f"✅ Found {len(sessions_after)} sessions after deletion")
    
    # Check that the specific session is gone
    deleted_session_exists = any(s['id'] == session_id for s in sessions_after)
    
    if deleted_session_exists:
        print(f"❌ Session {session_id} still exists after deletion!")
        return False
    
    if len(sessions_after) == len(sessions_before) - 1:
        print("✅ Session successfully deleted from database!")
        print(f"   Session count reduced from {len(sessions_before)} to {len(sessions_after)}")
    else:
        print(f"❌ Unexpected session count change: {len(sessions_before)} -> {len(sessions_after)}")
        return False
    
    print("\n✅ Backend delete functionality is working correctly!")
    return True

def show_frontend_instructions():
    """Show instructions for testing the frontend"""
    print("\n🌐 Frontend Delete Test Instructions:")
    print("1. Open http://localhost:3010 in your browser")
    print("2. Login with username: admin, password: password123")
    print("3. Look at the sidebar - you should see a list of chat sessions")
    print("4. 🎯 HOVER over any chat session")
    print("5. 👀 You should see a DELETE BUTTON (trash icon) appear on the right side")
    print("6. 🖱️  Click the delete button (trash icon)")
    print("7. 💬 Confirm the deletion in the confirmation dialog")
    print("8. ✨ The session should disappear from the sidebar immediately")
    print("9. 🔄 The page should stay responsive and other sessions should remain")
    print("\n🎉 If the delete button appears and works, the feature is complete!")
    
    print("\n📋 What to look for:")
    print("• Delete button only appears on hover")
    print("• Delete button has a trash icon")
    print("• Clicking shows a confirmation dialog")
    print("• Session disappears immediately after confirmation")
    print("• If the deleted session was active, it should switch to no session or another session")
    print("• Other sessions remain unaffected")

if __name__ == "__main__":
    backend_works = test_complete_delete_functionality()
    
    if backend_works:
        show_frontend_instructions()
    else:
        print("\n❌ Backend delete functionality has issues - fix backend first")
