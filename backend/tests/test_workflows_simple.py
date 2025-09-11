"""
Simplified integration tests that can run without Redis.

This version focuses on testing the core functionality without requiring
Redis/Celery setup, making it easier to run in environments where Redis
is not available.
"""

import pytest
import httpx
import uuid
from typing import Dict, Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models.user import User
from app.models.workflow import Workflow
from app.main import app

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test_workflows_simple.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    return engine


@pytest.fixture(scope="session")
def test_db_session(test_engine):
    """Create test database session factory."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    return TestingSessionLocal


@pytest.fixture(scope="function")
def db_session(test_engine, test_db_session):
    """Create a fresh database session for each test with rollback."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = test_db_session()
    
    yield session
    
    # Rollback and close
    session.rollback()
    session.close()
    
    # Drop all tables for clean state
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test HTTP client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_data():
    """Test user registration data."""
    return {
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "password": "TestPassword123",
        "confirm_password": "TestPassword123",
        "full_name": "Test User"
    }


@pytest.fixture(scope="function")
def authenticated_user(client, test_user_data):
    """Create and authenticate a test user."""
    # Register user
    register_response = client.post("/auth/register", json=test_user_data)
    assert register_response.status_code == 200
    
    # Login user
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    
    # Set authorization header for future requests
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    return {
        "user_data": test_user_data,
        "token_data": token_data,
        "access_token": access_token
    }


class TestUserAuthentication:
    """Test user registration and authentication flow."""
    
    def test_user_registration(self, client, test_user_data):
        """Test user registration endpoint."""
        response = client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 200
        user_data = response.json()
        
        assert user_data["email"] == test_user_data["email"]
        assert user_data["full_name"] == test_user_data["full_name"]
        assert user_data["is_active"] is True
        assert user_data["is_verified"] is True
        assert "id" in user_data
        assert "created_at" in user_data
    
    def test_user_login(self, client, test_user_data):
        """Test user login and JWT token generation."""
        # First register the user
        register_response = client.post("/auth/register", json=test_user_data)
        assert register_response.status_code == 200
        
        # Then login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert "expires_in" in token_data
        assert "user" in token_data
        
        # Verify user data in response
        user_data = token_data["user"]
        assert user_data["email"] == test_user_data["email"]
    
    def test_authenticated_endpoint_access(self, client, authenticated_user):
        """Test accessing protected endpoints with valid token."""
        response = client.get("/auth/me")
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == authenticated_user["user_data"]["email"]
    
    def test_unauthenticated_endpoint_access(self, client):
        """Test accessing protected endpoints without token."""
        response = client.get("/auth/me")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth


class TestWorkflowManagement:
    """Test workflow creation and management."""
    
    def test_workflow_creation(self, client, authenticated_user):
        """Test creating a new workflow."""
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow for integration testing",
            "canvas_data": {
                "nodes": [
                    {
                        "id": "trigger-1",
                        "type": "trigger",
                        "position": {"x": 100, "y": 100},
                        "data": {
                            "name": "Manual Trigger",
                            "config": {"type": "manual"}
                        }
                    }
                ],
                "edges": []
            }
        }
        
        response = client.post("/workflows", json=workflow_data)
        
        assert response.status_code == 200
        workflow = response.json()
        
        assert workflow["name"] == workflow_data["name"]
        assert workflow["description"] == workflow_data["description"]
        assert workflow["owner_id"] == authenticated_user["token_data"]["user"]["id"]
        assert workflow["is_active"] is True
        assert "id" in workflow
        assert "created_at" in workflow
    
    def test_workflow_retrieval(self, client, authenticated_user):
        """Test retrieving a specific workflow."""
        # First create a workflow
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "canvas_data": {"nodes": [], "edges": []}
        }
        
        create_response = client.post("/workflows", json=workflow_data)
        assert create_response.status_code == 200
        created_workflow = create_response.json()
        
        # Then retrieve it
        workflow_id = created_workflow["id"]
        response = client.get(f"/workflows/{workflow_id}")
        
        assert response.status_code == 200
        workflow = response.json()
        
        assert workflow["id"] == workflow_id
        assert workflow["name"] == created_workflow["name"]
        assert "nodes" in workflow
        assert "connections" in workflow
    
    def test_workflow_list(self, client, authenticated_user):
        """Test listing workflows for authenticated user."""
        # Create a workflow first
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "canvas_data": {"nodes": [], "edges": []}
        }
        
        create_response = client.post("/workflows", json=workflow_data)
        assert create_response.status_code == 200
        
        # List workflows
        response = client.get("/workflows")
        
        assert response.status_code == 200
        workflows = response.json()
        
        assert isinstance(workflows, list)
        assert len(workflows) >= 1
        
        # Find our created workflow
        workflow_ids = [w["id"] for w in workflows]
        assert create_response.json()["id"] in workflow_ids


class TestDatabaseIntegration:
    """Test database integration and data persistence."""
    
    def test_workflow_persistence(self, client, authenticated_user, db_session):
        """Test that workflow data is properly persisted in database."""
        # Create workflow via API
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "canvas_data": {"nodes": [], "edges": []}
        }
        
        response = client.post("/workflows", json=workflow_data)
        assert response.status_code == 200
        workflow_data = response.json()
        
        # Verify in database
        db_workflow = db_session.query(Workflow).filter(Workflow.id == workflow_data["id"]).first()
        assert db_workflow is not None
        assert db_workflow.name == workflow_data["name"]
        assert db_workflow.description == workflow_data["description"]
        assert db_workflow.owner_id == authenticated_user["token_data"]["user"]["id"]


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_workflow_not_found(self, client, authenticated_user):
        """Test accessing non-existent workflow."""
        response = client.get("/workflows/99999")
        assert response.status_code == 404
    
    def test_unauthorized_workflow_access(self, client):
        """Test accessing workflow from different user."""
        # Create first user and workflow
        user1_data = {
            "email": f"user1_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "full_name": "User 1"
        }
        
        # Register first user
        register_response = client.post("/auth/register", json=user1_data)
        assert register_response.status_code == 200
        
        # Login first user
        login_data = {
            "email": user1_data["email"],
            "password": user1_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        
        # Create workflow with first user
        workflow_data = {
            "name": "User 1 Workflow",
            "description": "A workflow",
            "canvas_data": {"nodes": [], "edges": []}
        }
        
        create_response = client.post("/workflows", json=workflow_data)
        assert create_response.status_code == 200
        workflow_id = create_response.json()["id"]
        
        # Create second user
        user2_data = {
            "email": f"user2_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "full_name": "User 2"
        }
        
        # Register second user
        register_response = client.post("/auth/register", json=user2_data)
        assert register_response.status_code == 200
        
        # Login second user
        login_data = {
            "email": user2_data["email"],
            "password": user2_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        
        # Try to access first user's workflow
        response = client.get(f"/workflows/{workflow_id}")
        
        assert response.status_code == 404  # Should not find workflow


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
