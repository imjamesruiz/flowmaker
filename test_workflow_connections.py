#!/usr/bin/env python3
"""
Test script for workflow connections and execution
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def login():
    """Login and get auth token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def create_test_workflow(token):
    """Create a test workflow"""
    headers = {"Authorization": f"Bearer {token}"}
    
    workflow_data = {
        "name": "Test Workflow - Connections",
        "description": "Testing workflow connections and execution"
    }
    
    response = requests.post(f"{BASE_URL}/workflows", json=workflow_data, headers=headers)
    
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print(f"Failed to create workflow: {response.status_code} - {response.text}")
        return None

def test_workflow_connections(token, workflow_id):
    """Test workflow with nodes and connections"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple workflow: Trigger -> Transformer -> Condition -> Action
    workflow_data = {
        "id": str(workflow_id),
        "name": "Test Workflow - Connections",
        "nodes": [
            {
                "id": "trigger_1",
                "type": "trigger",
                "position": {"x": 100, "y": 100},
                "data": {
                    "name": "HTTP Trigger",
                    "config": {"method": "POST"}
                }
            },
            {
                "id": "transformer_1",
                "type": "transformer",
                "position": {"x": 300, "y": 100},
                "data": {
                    "name": "Transform Data",
                    "config": {"type": "to_uppercase"}
                }
            },
            {
                "id": "condition_1",
                "type": "condition",
                "position": {"x": 500, "y": 100},
                "data": {
                    "name": "Check Condition",
                    "config": {"condition": "len(str(input)) > 5"}
                }
            },
            {
                "id": "action_1",
                "type": "action",
                "position": {"x": 700, "y": 50},
                "data": {
                    "name": "Send Email",
                    "config": {"to": "user@example.com"}
                }
            },
            {
                "id": "webhook_1",
                "type": "webhook",
                "position": {"x": 700, "y": 150},
                "data": {
                    "name": "Call Webhook",
                    "config": {"url": "https://api.example.com/webhook"}
                }
            }
        ],
        "edges": [
            {
                "id": "e_trigger_1-out_transformer_1-in",
                "source": "trigger_1",
                "sourceHandle": "out",
                "target": "transformer_1",
                "targetHandle": "in"
            },
            {
                "id": "e_transformer_1-out_condition_1-in",
                "source": "transformer_1",
                "sourceHandle": "out",
                "target": "condition_1",
                "targetHandle": "in"
            },
            {
                "id": "e_condition_1-true_action_1-in",
                "source": "condition_1",
                "sourceHandle": "true",
                "target": "action_1",
                "targetHandle": "in",
                "label": "true"
            },
            {
                "id": "e_condition_1-false_webhook_1-in",
                "source": "condition_1",
                "sourceHandle": "false",
                "target": "webhook_1",
                "targetHandle": "in",
                "label": "false"
            }
        ]
    }
    
    # Save workflow
    response = requests.put(f"{BASE_URL}/workflows/{workflow_id}/bulk", json=workflow_data, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to save workflow: {response.status_code} - {response.text}")
        return False
    
    print("✅ Workflow saved successfully")
    
    # Validate workflow
    response = requests.post(f"{BASE_URL}/workflows/{workflow_id}/validate", json=workflow_data, headers=headers)
    
    if response.status_code == 200:
        validation = response.json()
        if validation["valid"]:
            print("✅ Workflow validation passed")
        else:
            print(f"❌ Workflow validation failed: {validation['errors']}")
            return False
    else:
        print(f"❌ Validation request failed: {response.status_code} - {response.text}")
        return False
    
    # Test workflow execution
    test_data = {
        "test_mode": True,
        "trigger_data": {"message": "Hello World", "user": "testuser"}
    }
    
    response = requests.post(f"{BASE_URL}/workflows/{workflow_id}/test", json=test_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            print("✅ Workflow execution successful")
            print(f"📊 Execution logs: {len(result['logs'])} nodes executed")
            for log in result["logs"]:
                print(f"  - {log['node_name']} ({log['node_type']}): {log['status']}")
                if log.get('output'):
                    print(f"    Output: {log['output']}")
        else:
            print(f"❌ Workflow execution failed: {result.get('error')}")
            return False
    else:
        print(f"❌ Execution request failed: {response.status_code} - {response.text}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 Testing Worqly Workflow Connections and Execution")
    print("=" * 60)
    
    # Login
    print("🔐 Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Please ensure the backend is running and test user exists.")
        return
    
    print("✅ Login successful")
    
    # Create workflow
    print("\n📝 Creating test workflow...")
    workflow_id = create_test_workflow(token)
    if not workflow_id:
        print("❌ Failed to create workflow")
        return
    
    print(f"✅ Workflow created with ID: {workflow_id}")
    
    # Test connections and execution
    print("\n🔗 Testing workflow connections and execution...")
    success = test_workflow_connections(token, workflow_id)
    
    if success:
        print("\n🎉 All tests passed! Workflow connections and execution are working correctly.")
    else:
        print("\n💥 Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
