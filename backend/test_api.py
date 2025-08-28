import requests
import json

# Test the login endpoint
login_data = {
    "email": "admin@example.com",
    "password": "admin123"
}

response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
print("Login response:", response.status_code)
print("Login response:", response.json())

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the bulk update endpoint with valid data
    test_data = {
        "name": "Test Workflow",
        "description": "Test description",
        "nodes": [
            {
                "id": "node1",
                "type": "trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "name": "Test Trigger",
                    "config": {}
                }
            }
        ],
        "edges": []
    }
    
    # First, let's create a workflow
    create_data = {
        "name": "Test Workflow",
        "description": "Test description"
    }
    
    create_response = requests.post("http://localhost:8000/api/v1/workflows", json=create_data, headers=headers)
    print("Create workflow response:", create_response.status_code)
    print("Create workflow response:", create_response.json())
    
    if create_response.status_code == 200:
        workflow_id = create_response.json()["id"]
        
        # Now test the bulk update
        bulk_response = requests.put(f"http://localhost:8000/api/v1/workflows/{workflow_id}/bulk", json=test_data, headers=headers)
        print("Bulk update response:", bulk_response.status_code)
        print("Bulk update response:", bulk_response.text)
        
        if bulk_response.status_code != 200:
            print("Error details:", bulk_response.json())
else:
    print("Failed to login")
