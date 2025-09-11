"""
Shared pytest fixtures and configuration for workflow automation tests.
"""

import pytest
import os
import tempfile
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from redis import Redis
from celery import Celery

from app.database import Base
from app.config import settings


@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL."""
    return "sqlite:///./test_workflows.db"


@pytest.fixture(scope="session")
def test_redis_url():
    """Get test Redis URL."""
    return "redis://localhost:6379/1"


@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """Create test database engine."""
    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    return engine


@pytest.fixture(scope="session")
def test_db_session_factory(test_engine):
    """Create test database session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine, test_db_session_factory):
    """Create a fresh database session for each test with rollback."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = test_db_session_factory()
    
    yield session
    
    # Rollback and close
    session.rollback()
    session.close()
    
    # Drop all tables for clean state
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_redis(test_redis_url):
    """Create test Redis client with separate namespace."""
    redis_client = Redis.from_url(test_redis_url, decode_responses=True)
    
    # Clear test database
    redis_client.flushdb()
    
    yield redis_client
    
    # Clean up
    redis_client.flushdb()
    redis_client.close()


@pytest.fixture(scope="function")
def test_celery_app(test_redis_url):
    """Create test Celery app with eager execution."""
    test_celery = Celery(
        "test_workflows",
        broker=test_redis_url,
        backend=test_redis_url,
        include=["app.core.tasks"]
    )
    
    test_celery.conf.update(
        task_always_eager=True,  # Execute tasks synchronously
        task_eager_propagates=True,  # Propagate exceptions
        result_backend=test_redis_url,
        broker_url=test_redis_url,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    
    return test_celery


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, test_database_url, test_redis_url):
    """Set up test environment variables."""
    monkeypatch.setenv("DATABASE_URL", test_database_url)
    monkeypatch.setenv("REDIS_URL", test_redis_url)
    monkeypatch.setenv("CELERY_BROKER_URL", test_redis_url)
    monkeypatch.setenv("CELERY_RESULT_BACKEND", test_redis_url)
    monkeypatch.setenv("USE_SUPABASE_AUTH", "false")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DEBUG", "true")
