#!/usr/bin/env python3
"""
Test script to verify that delete conversation functionality works
"""
import requests


def test_delete_functionality():
    """Test that the delete functionality works correctly"""
    print("🧪 Testing delete conversation functionality...")
    
    # Login to get token
    login_data = {'username': 'admin', 'password': 'password123'}
    login_response = requests.post('http://localhost:8000/auth/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
        
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get sessions before
    sessions_response = requests.get('http://localhost:8000/chat/sessions', headers=headers)
    
    if sessions_response.status_code != 200:
        print(f"❌ Failed to get sessions: {sessions_response.status_code}")
        return False
        
    sessions_before = sessions_response.json()
    print(f"✅ Found {len(sessions_before)} sessions before deletion")
    
    if len(sessions_before) == 0:
        print("❌ No sessions to delete")
        return False
    
    # Find a session to delete (pick one that's not the first one)
    target_session = None
    for session in sessions_before[1:]:  # Skip first session to be safe
        if session.get('title') != 'New Chat':
            target_session = session
            break
    
    if not target_session:
        print("❌ No suitable session found for deletion test")
        return False
    
    print(f"🗑️  Target session for deletion: ID {target_session['id']}, Title: '{target_session['title']}'")
    
    # Delete the session
    delete_response = requests.delete(
        f'http://localhost:8000/chat/sessions/{target_session["id"]}',
        headers=headers
    )
    
    if delete_response.status_code != 200:
        print(f"❌ Failed to delete session: {delete_response.status_code}")
        print(f"   Response: {delete_response.text}")
        return False
    
    print("✅ Delete request successful!")
    
    # Get sessions after deletion
    sessions_response = requests.get('http://localhost:8000/chat/sessions', headers=headers)
    sessions_after = sessions_response.json()
    
    print(f"✅ Found {len(sessions_after)} sessions after deletion")
    
    # Verify the session was actually deleted
    deleted_session_ids = [s['id'] for s in sessions_after]
    if target_session['id'] in deleted_session_ids:
        print("❌ Session was not actually deleted from the database")
        return False
    
    print("✅ Session successfully deleted from database!")
    print(f"   Session count reduced from {len(sessions_before)} to {len(sessions_after)}")
    
    return True

def test_frontend_manually():
    """Manual test instructions for frontend delete functionality"""
    print("\n🌐 Manual Frontend Delete Test Instructions:")
    print("1. Open http://localhost:3010 in your browser")
    print("2. Login with username: admin, password: password123")
    print("3. Look at the sidebar - you should see a list of chat sessions")
    print("4. Hover over any chat session")
    print("5. You should see a delete button (trash icon) appear on the right")
    print("6. Click the delete button")
    print("7. Confirm the deletion in the dialog")
    print("8. The session should disappear from the sidebar immediately")
    print("9. If the delete button appears and works, the feature is complete! ✅")

if __name__ == "__main__":
    print("🗑️  Testing Delete Conversation Functionality\n")
    
    # Test backend first
    backend_works = test_delete_functionality()
    
    if backend_works:
        print("\n✅ Backend delete functionality is working correctly!")
        test_frontend_manually()
    else:
        print("\n❌ Backend delete functionality has issues - fix backend first")
