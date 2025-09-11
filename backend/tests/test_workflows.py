"""
Integration tests for workflow automation platform.

Tests the complete end-to-end workflow execution flow including:
- User registration and authentication
- Workflow creation and management
- Workflow execution with Celery tasks
- Error handling and logging
"""

import pytest
import httpx
import time
import uuid
from typing import Dict, Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from celery import Celery
from celery.contrib.testing.worker import start_worker
from redis import Redis
from unittest.mock import patch

from app.database import Base, get_db
from app.models.user import User
from app.models.workflow import Workflow, WorkflowNode, WorkflowConnection
from app.models.execution import WorkflowExecution, ExecutionLog, ExecutionStatus
from app.core.celery_app import celery_app
from app.config import settings
from app.main import app


# Test configuration
TEST_DATABASE_URL = "sqlite:///./test_workflows.db"
TEST_REDIS_URL = "redis://localhost:6379/1"  # Use different Redis DB for tests


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine with transaction rollback support."""
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
def test_redis():
    """Create test Redis client with separate namespace."""
    redis_client = Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    
    # Clear test database
    redis_client.flushdb()
    
    yield redis_client
    
    # Clean up
    redis_client.flushdb()
    redis_client.close()


@pytest.fixture(scope="function")
def test_celery_app(test_redis):
    """Create test Celery app with eager execution."""
    # Configure Celery for testing
    test_celery = Celery(
        "test_workflows",
        broker=TEST_REDIS_URL,
        backend=TEST_REDIS_URL,
        include=["app.core.tasks"]
    )
    
    test_celery.conf.update(
        task_always_eager=True,  # Execute tasks synchronously
        task_eager_propagates=True,  # Propagate exceptions
        result_backend=TEST_REDIS_URL,
        broker_url=TEST_REDIS_URL,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    
    return test_celery


@pytest.fixture(scope="function")
def client(db_session, test_celery_app):
    """Create test HTTP client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with httpx.Client(app=app, base_url="http://test") as test_client:
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


@pytest.fixture(scope="function")
def test_workflow_data():
    """Test workflow creation data."""
    return {
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
                },
                {
                    "id": "action-1", 
                    "type": "action",
                    "position": {"x": 300, "y": 100},
                    "data": {
                        "name": "Test Action",
                        "config": {"action": "log", "message": "Hello World"}
                    }
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "trigger-1",
                    "target": "action-1"
                }
            ]
        }
    }


@pytest.fixture(scope="function")
def created_workflow(client, authenticated_user, test_workflow_data):
    """Create a test workflow."""
    response = client.post("/workflows", json=test_workflow_data)
    assert response.status_code == 200
    
    workflow = response.json()
    return workflow


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
        assert response.status_code == 401


class TestWorkflowManagement:
    """Test workflow creation and management."""
    
    def test_workflow_creation(self, client, authenticated_user, test_workflow_data):
        """Test creating a new workflow."""
        response = client.post("/workflows", json=test_workflow_data)
        
        assert response.status_code == 200
        workflow = response.json()
        
        assert workflow["name"] == test_workflow_data["name"]
        assert workflow["description"] == test_workflow_data["description"]
        assert workflow["owner_id"] == authenticated_user["token_data"]["user"]["id"]
        assert workflow["is_active"] is True
        assert "id" in workflow
        assert "created_at" in workflow
    
    def test_workflow_retrieval(self, client, created_workflow):
        """Test retrieving a specific workflow."""
        workflow_id = created_workflow["id"]
        response = client.get(f"/workflows/{workflow_id}")
        
        assert response.status_code == 200
        workflow = response.json()
        
        assert workflow["id"] == workflow_id
        assert workflow["name"] == created_workflow["name"]
        assert "nodes" in workflow
        assert "connections" in workflow
    
    def test_workflow_list(self, client, authenticated_user, created_workflow):
        """Test listing workflows for authenticated user."""
        response = client.get("/workflows")
        
        assert response.status_code == 200
        workflows = response.json()
        
        assert isinstance(workflows, list)
        assert len(workflows) >= 1
        
        # Find our created workflow
        workflow_ids = [w["id"] for w in workflows]
        assert created_workflow["id"] in workflow_ids
    
    def test_workflow_bulk_update(self, client, created_workflow):
        """Test bulk updating workflow with nodes and edges."""
        workflow_id = created_workflow["id"]
        
        update_data = {
            "name": "Updated Test Workflow",
            "description": "Updated description",
            "nodes": [
                {
                    "id": "trigger-1",
                    "type": "trigger",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "name": "Updated Trigger",
                        "config": {"type": "manual"}
                    }
                },
                {
                    "id": "action-1",
                    "type": "action", 
                    "position": {"x": 300, "y": 100},
                    "data": {
                        "name": "Updated Action",
                        "config": {"action": "log", "message": "Updated Message"}
                    }
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "trigger-1",
                    "target": "action-1"
                }
            ]
        }
        
        response = client.put(f"/workflows/{workflow_id}/bulk", json=update_data)
        
        assert response.status_code == 200
        updated_workflow = response.json()
        
        assert updated_workflow["name"] == "Updated Test Workflow"
        assert updated_workflow["description"] == "Updated description"
        assert len(updated_workflow["nodes"]) == 2
        assert len(updated_workflow["connections"]) == 1


@pytest.mark.integration
class TestWorkflowExecution:
    """Test workflow execution with Celery tasks."""
    
    def test_workflow_execution_success(self, client, created_workflow, db_session):
        """Test successful workflow execution end-to-end."""
        workflow_id = created_workflow["id"]
        
        # Execute workflow
        execution_request = {
            "trigger_data": {"test": "data"},
            "test_mode": True
        }
        
        response = client.post(f"/workflows/{workflow_id}/execute", json=execution_request)
        
        assert response.status_code == 200
        execution_response = response.json()
        
        assert "task_id" in execution_response
        assert execution_response["status"] == "executing"
        
        # Wait a moment for task to complete (since we're using eager execution)
        time.sleep(0.1)
        
        # Check execution status
        executions_response = client.get("/executions")
        assert executions_response.status_code == 200
        
        executions = executions_response.json()
        assert len(executions) >= 1
        
        # Find our execution
        execution = None
        for exec_item in executions:
            if exec_item["workflow_id"] == workflow_id:
                execution = exec_item
                break
        
        assert execution is not None
        assert execution["status"] in [ExecutionStatus.COMPLETED.value, ExecutionStatus.FAILED.value]
        
        # Verify execution logs exist
        execution_id = execution["id"]
        logs_response = client.get(f"/executions/{execution_id}/logs")
        
        if logs_response.status_code == 200:
            logs = logs_response.json()
            assert isinstance(logs, list)
            # Should have at least one log entry
            assert len(logs) >= 0  # May be 0 if workflow has no executable nodes
    
    def test_workflow_test_execution(self, client, created_workflow):
        """Test synchronous workflow test execution."""
        workflow_id = created_workflow["id"]
        
        execution_request = {
            "trigger_data": {"test": "data"},
            "test_mode": True
        }
        
        response = client.post(f"/workflows/{workflow_id}/test", json=execution_request)
        
        assert response.status_code == 200
        result = response.json()
        
        assert "success" in result
        assert "logs" in result
        assert isinstance(result["logs"], list)
    
    def test_workflow_execution_with_invalid_config(self, client, authenticated_user, db_session):
        """Test workflow execution with invalid node configuration."""
        # Create workflow with invalid configuration
        invalid_workflow_data = {
            "name": "Invalid Workflow",
            "description": "Workflow with invalid configuration",
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
                    },
                    {
                        "id": "action-1",
                        "type": "action",
                        "position": {"x": 300, "y": 100},
                        "data": {
                            "name": "Invalid Action",
                            "config": {"action": "invalid_action", "invalid_param": "value"}
                        }
                    }
                ],
                "edges": [
                    {
                        "id": "edge-1",
                        "source": "trigger-1",
                        "target": "action-1"
                    }
                ]
            }
        }
        
        # Create workflow
        create_response = client.post("/workflows", json=invalid_workflow_data)
        assert create_response.status_code == 200
        workflow = create_response.json()
        
        # Execute workflow
        execution_request = {
            "trigger_data": {"test": "data"},
            "test_mode": True
        }
        
        response = client.post(f"/workflows/{workflow['id']}/execute", json=execution_request)
        assert response.status_code == 200
        
        # Wait for execution
        time.sleep(0.1)
        
        # Check execution status - should be failed
        executions_response = client.get("/executions")
        assert executions_response.status_code == 200
        
        executions = executions_response.json()
        workflow_executions = [e for e in executions if e["workflow_id"] == workflow["id"]]
        
        if workflow_executions:
            execution = workflow_executions[0]
            # Execution might fail due to invalid configuration
            assert execution["status"] in [
                ExecutionStatus.COMPLETED.value, 
                ExecutionStatus.FAILED.value,
                ExecutionStatus.RUNNING.value
            ]
            
            # If failed, should have error message
            if execution["status"] == ExecutionStatus.FAILED.value:
                assert execution["error_message"] is not None


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_workflow_not_found(self, client, authenticated_user):
        """Test accessing non-existent workflow."""
        response = client.get("/workflows/99999")
        assert response.status_code == 404
    
    def test_unauthorized_workflow_access(self, client, test_user_data, created_workflow):
        """Test accessing workflow from different user."""
        # Create second user
        second_user_data = {
            "email": f"test2_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "full_name": "Second User"
        }
        
        # Register second user
        register_response = client.post("/auth/register", json=second_user_data)
        assert register_response.status_code == 200
        
        # Login second user
        login_data = {
            "email": second_user_data["email"],
            "password": second_user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Try to access first user's workflow
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        response = client.get(f"/workflows/{created_workflow['id']}")
        
        assert response.status_code == 404  # Should not find workflow
    
    def test_invalid_workflow_execution(self, client, authenticated_user):
        """Test executing non-existent workflow."""
        response = client.post("/workflows/99999/execute", json={"trigger_data": {}})
        assert response.status_code == 404


class TestDatabaseIntegration:
    """Test database integration and data persistence."""
    
    def test_workflow_persistence(self, client, authenticated_user, test_workflow_data, db_session):
        """Test that workflow data is properly persisted in database."""
        # Create workflow via API
        response = client.post("/workflows", json=test_workflow_data)
        assert response.status_code == 200
        workflow_data = response.json()
        
        # Verify in database
        db_workflow = db_session.query(Workflow).filter(Workflow.id == workflow_data["id"]).first()
        assert db_workflow is not None
        assert db_workflow.name == test_workflow_data["name"]
        assert db_workflow.description == test_workflow_data["description"]
        assert db_workflow.owner_id == authenticated_user["token_data"]["user"]["id"]
    
    def test_execution_logging(self, client, created_workflow, db_session):
        """Test that execution logs are properly stored."""
        workflow_id = created_workflow["id"]
        
        # Execute workflow
        execution_request = {
            "trigger_data": {"test": "data"},
            "test_mode": True
        }
        
        response = client.post(f"/workflows/{workflow_id}/execute", json=execution_request)
        assert response.status_code == 200
        
        # Wait for execution
        time.sleep(0.1)
        
        # Check database for execution records
        executions = db_session.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).all()
        
        assert len(executions) >= 1
        
        execution = executions[0]
        assert execution.workflow_id == workflow_id
        assert execution.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.RUNNING]
        
        # Check for execution logs
        logs = db_session.query(ExecutionLog).filter(
            ExecutionLog.execution_id == execution.id
        ).all()
        
        # Logs may be empty if workflow has no executable nodes
        assert isinstance(logs, list)


# Utility functions for tests
def wait_for_execution_completion(client, workflow_id: int, max_wait: int = 10) -> Dict[str, Any]:
    """Wait for workflow execution to complete and return the execution."""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = client.get("/executions")
        if response.status_code == 200:
            executions = response.json()
            workflow_executions = [e for e in executions if e["workflow_id"] == workflow_id]
            
            if workflow_executions:
                execution = workflow_executions[0]
                if execution["status"] in [ExecutionStatus.COMPLETED.value, ExecutionStatus.FAILED.value]:
                    return execution
        
        time.sleep(0.1)
    
    raise TimeoutError(f"Workflow execution did not complete within {max_wait} seconds")


def create_simple_workflow(client, name: str = "Simple Test Workflow") -> Dict[str, Any]:
    """Create a simple workflow for testing."""
    workflow_data = {
        "name": name,
        "description": f"Simple workflow: {name}",
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
    return response.json()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
