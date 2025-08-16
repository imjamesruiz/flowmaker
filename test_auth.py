#!/usr/bin/env python3
"""
Test script for JWT authentication system
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
        "confirm_password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    
    if response.status_code == 200:
        print("✅ Registration successful!")
        user = response.json()
        print(f"   User ID: {user['id']}")
        print(f"   Email: {user['email']}")
        return True
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        token_data = response.json()
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Expires in: {token_data['expires_in']} seconds")
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\nTesting protected endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ Protected endpoint access successful!")
        user = response.json()
        print(f"   User: {user['full_name']} ({user['email']})")
        return True
    else:
        print(f"❌ Protected endpoint access failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_logout(token):
    """Test user logout"""
    print("\nTesting user logout...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    
    if response.status_code == 200:
        print("✅ Logout successful!")
        return True
    else:
        print(f"❌ Logout failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    """Run all authentication tests"""
    print("🧪 Testing JWT Authentication System")
    print("=" * 50)
    
    # Test registration
    if not test_register():
        print("Registration failed, stopping tests.")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("Login failed, stopping tests.")
        return
    
    # Test protected endpoint
    test_protected_endpoint(token)
    
    # Test logout
    test_logout(token)
    
    # Test that token is now invalid
    print("\nTesting that token is invalid after logout...")
    if not test_protected_endpoint(token):
        print("✅ Token correctly invalidated after logout!")
    else:
        print("❌ Token still valid after logout!")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication tests completed!")

if __name__ == "__main__":
    main()
