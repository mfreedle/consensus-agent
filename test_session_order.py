#!/usr/bin/env python3
"""
Test script to verify session ordering
"""
import requests
from datetime import datetime

def test_session_ordering():
    """Test that sessions are ordered from newest to oldest"""
    print("🧪 Testing session ordering...")
    
    # Login to get token
    login_data = {'username': 'admin', 'password': 'password123'}
    login_response = requests.post('http://localhost:8000/auth/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
        
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get sessions
    sessions_response = requests.get('http://localhost:8000/chat/sessions', headers=headers)
    
    if sessions_response.status_code != 200:
        print(f"❌ Failed to get sessions: {sessions_response.status_code}")
        return False
        
    sessions = sessions_response.json()
    print(f"✅ Found {len(sessions)} sessions")
    
    # Check the first few sessions and their timestamps
    print("\n📋 First 5 sessions (should be ordered newest to oldest):")
    for i, session in enumerate(sessions[:5]):
        created_at = session.get('created_at', 'N/A')
        updated_at = session.get('updated_at', 'N/A') 
        title = session.get('title', 'N/A')
        print(f"  {i+1}. ID: {session['id']}, Title: '{title}'")
        print(f"     Created: {created_at}")
        print(f"     Updated: {updated_at}")
        print()
    
    # Check if they are in descending order by comparing timestamps
    is_ordered = True
    for i in range(len(sessions) - 1):
        current = sessions[i]
        next_session = sessions[i + 1]
        
        # Get the effective timestamp (updated_at or created_at)
        current_time = current.get('updated_at') or current.get('created_at')
        next_time = next_session.get('updated_at') or next_session.get('created_at')
        
        if current_time and next_time:
            current_dt = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
            next_dt = datetime.fromisoformat(next_time.replace('Z', '+00:00'))
            
            if current_dt < next_dt:  # Should be newer (greater) than next
                is_ordered = False
                print(f"❌ Ordering issue: Session {current['id']} ({current_time}) is older than session {next_session['id']} ({next_time})")
                break
    
    if is_ordered:
        print("✅ Sessions are correctly ordered from newest to oldest!")
    else:
        print("❌ Sessions are NOT correctly ordered")
    
    return is_ordered

if __name__ == "__main__":
    test_session_ordering()
