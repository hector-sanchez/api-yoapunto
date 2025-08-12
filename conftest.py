"""
Test Configuration (conftest.py)

This file contains pytest fixtures and configuration that are shared across all tests.
Fixtures are reusable components that set up test environments - like creating
test databases, test clients, etc.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
# Import models the SAME way as main.py does - this registers them with SQLAlchemy
from app.models import club

# Test database configuration
# We use a separate SQLite file for tests to avoid interfering with real data
TEST_DATABASE_URL = "sqlite:///./test_yoapunto.db"

# Create a separate database engine just for tests
# This ensures tests are completely isolated from your main application database
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """
    Override function for the database dependency in tests

    This replaces the normal get_db() function during testing,
    so that tests use the test database instead of the real one.
    """
    try:
        db = TestingSessionLocal()
        yield db  # Provide the test database session
    finally:
        db.close()

@pytest.fixture(scope="function")
def db():
    """
    Database fixture for tests that need direct database access

    This fixture:
    1. Creates fresh database tables for each test
    2. Provides a database session
    3. Cleans up by dropping tables after the test

    scope="function" means a new database is created for each test function,
    ensuring complete test isolation.
    """
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    # Create fresh tables
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db  # This is what gets passed to test functions that use this fixture
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    """
    FastAPI test client fixture for API endpoint tests

    This fixture:
    1. Creates fresh database tables
    2. Overrides the database dependency to use test database
    3. Provides a test client that can make HTTP requests to your API
    4. Cleans up after each test

    The test client lets you make requests like:
    response = client.get("/api/v1/clubs/")
    """
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    # Create fresh tables for this test
    Base.metadata.create_all(bind=test_engine)

    # Override the database dependency to use test database
    # This is FastAPI's dependency injection in action - we're swapping out
    # the real database for our test database
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client  # This is what gets passed to test functions

    # Clean up after test
    app.dependency_overrides.clear()  # Remove the override
    Base.metadata.drop_all(bind=test_engine)  # Clean up test data

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """
    Session-level fixture to clean up test database file

    autouse=True means this runs automatically without being explicitly requested.
    scope="session" means it runs once for the entire test session.
    This ensures the test database file is deleted after all tests complete.
    """
    yield  # Let all tests run first
    # Remove test database file after all tests are done
    if os.path.exists("test_yoapunto.db"):
        os.remove("test_yoapunto.db")
