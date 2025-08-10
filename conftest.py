import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
# Import models the SAME way as main.py does
from app.models import club

# Test database URL - using file-based SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test_yoapunto.db"

# Create a single test engine that will be shared
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    # Create fresh tables
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up after test
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client():
    """Create a test client with database dependency override"""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    # Create fresh tables for this test
    Base.metadata.create_all(bind=test_engine)

    # Override the database dependency to use test database
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up after test
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Clean up test database file after all tests"""
    yield
    # Remove test database file after all tests are done
    if os.path.exists("test_yoapunto.db"):
        os.remove("test_yoapunto.db")
