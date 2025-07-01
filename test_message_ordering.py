#!/usr/bin/env python3
"""
Test script to send a message to an existing session and verify ordering
"""
import requests
from datetime import datetime
import time

def send_test_message():
    """Send a test message to an existing session and verify ordering"""
    print("🧪 Testing message sending and ordering update...")
    
    # Login to get token
    login_data = {'username': 'admin', 'password': 'password123'}
    login_response = requests.post('http://localhost:8000/auth/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
        
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get sessions and find one to test with
    sessions_response = requests.get('http://localhost:8000/chat/sessions', headers=headers)
    
    if sessions_response.status_code != 200:
        print(f"❌ Failed to get sessions: {sessions_response.status_code}")
        return False
        
    sessions = sessions_response.json()
    print(f"✅ Found {len(sessions)} sessions")
    
    # Find a session that's not the first one (so we can see it move to the top)
    target_session = None
    for session in sessions[2:]:  # Skip first 2 sessions
        if session.get('title') != 'New Chat':
            target_session = session
            break
    
    if not target_session:
        print("❌ No suitable session found for testing")
        return False
    
    print(f"📝 Target session: ID {target_session['id']}, Title: '{target_session['title']}'")
    print(f"   Current position in list: {sessions.index(target_session) + 1}")
    
    # Send a test message via REST API
    message_data = {
        'message': f'Test message sent at {datetime.now().isoformat()}',
        'session_id': target_session["id"],
        'model_selection': {
            'models': ['openai'],
            'consensus_mode': True
        }
    }
    
    message_response = requests.post(
        'http://localhost:8000/chat/message',
        json=message_data,
        headers=headers
    )
    
    if message_response.status_code != 200:
        print(f"❌ Failed to send message: {message_response.status_code}")
        print(f"   Response: {message_response.text}")
        return False
    
    print("✅ Message sent successfully!")
    
    # Wait a moment for the database to update
    time.sleep(1)
    
    # Get sessions again and check new ordering
    sessions_response = requests.get('http://localhost:8000/chat/sessions', headers=headers)
    updated_sessions = sessions_response.json()
    
    # Check if the target session moved to the top
    if updated_sessions[0]['id'] == target_session['id']:
        print("✅ Session correctly moved to the top of the list!")
        print(f"   New updated_at: {updated_sessions[0].get('updated_at', 'None')}")
        return True
    else:
        print("❌ Session did not move to the top")
        print(f"   Top session is now: ID {updated_sessions[0]['id']}, Title: '{updated_sessions[0]['title']}'")
        print(f"   Target session is now at position: {[s['id'] for s in updated_sessions].index(target_session['id']) + 1}")
        return False

if __name__ == "__main__":
    send_test_message()
