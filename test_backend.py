import requests
import json

# Test backend connectivity
def test_backend():
    base_url = "http://localhost:8000"
    
    try:
        # Test if server is running
        response = requests.get(f"{base_url}/docs")
        print(f"✅ Backend server is running (status: {response.status_code})")
        
        # Test auth endpoints
        auth_url = f"{base_url}/api/v1/auth"
        
        # Test registration
        register_data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123",
            "confirm_password": "testpassword123"
        }
        
        response = requests.post(f"{auth_url}/register", json=register_data)
        print(f"📝 Registration test: {response.status_code}")
        if response.status_code == 200:
            print("✅ Registration successful")
        elif response.status_code == 422:
            print("⚠️  User might already exist")
        else:
            print(f"❌ Registration failed: {response.text}")
        
        # Test login
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{auth_url}/login", json=login_data)
        print(f"🔐 Login test: {response.status_code}")
        if response.status_code == 200:
            print("✅ Login successful")
            token = response.json().get("access_token")
            print(f"Token received: {token[:20]}..." if token else "No token")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running on http://localhost:8000")
        print("Please start the backend server first:")
        print("cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error testing backend: {e}")

if __name__ == "__main__":
    test_backend()
