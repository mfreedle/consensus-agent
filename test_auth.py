#!/usr/bin/env python3
"""
Test script for the authentication system
"""
import requests

BASE_URL = "http://localhost:8000/api/auth"

def test_registration():
    """Test user registration with email"""
    print("Testing user registration...")
    
    data = {
        "username": "finaltest2025",
        "email": "finaltest2025@example.com", 
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=data)
        print(f"Registration status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Registration failed: {e}")
        return False

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    data = {
        "username": "finaltest2025",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=data)
        print(f"Login status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            return result.get("access_token")
        return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_user_info(token):
    """Test getting user info"""
    print("\nTesting user info retrieval...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"User info status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"User info failed: {e}")
        return False

def test_password_change(token):
    """Test password change"""
    print("\nTesting password change...")
    
    data = {
        "current_password": "testpass123",
        "new_password": "newpass123"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.put(f"{BASE_URL}/change-password", json=data, headers=headers)
        print(f"Password change status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Password change failed: {e}")
        return False

def main():
    print("=== Authentication System Test ===\n")
    
    # Test registration
    if not test_registration():
        print("Registration failed, stopping tests")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("Login failed, stopping tests")
        return
    
    # Test user info
    test_user_info(token)
    
    # Test password change
    test_password_change(token)
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main()
