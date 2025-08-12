"""
Database Configuration Module

This file sets up the database connection, session management, and provides
the foundational SQLAlchemy components used throughout the application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This allows us to keep sensitive configuration (like database URLs) out of our code
load_dotenv()

# Get database URL from environment variable, with a fallback default
# In production, you'd set DATABASE_URL as an environment variable
# For development, we default to a local SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./yoapunto.db")

# Create the SQLAlchemy engine
# The engine is responsible for connecting to the database
# For SQLite, we need check_same_thread=False to allow multiple threads
engine = create_engine(DATABASE_URL)

# Create a session factory
# Sessions are used to interact with the database (queries, inserts, updates, etc.)
# autocommit=False means we control when changes are saved to the database
# autoflush=False means we control when pending changes are sent to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the base class for our database models
# All our model classes (like Club) will inherit from this Base class
Base = declarative_base()

# Dependency function for FastAPI
# This function provides a database session to our API endpoints
# The 'yield' makes this a generator function - FastAPI will automatically
# close the session when the request is finished
def get_db():
    """
    Database session dependency for FastAPI endpoints

    This function creates a new database session for each request,
    and ensures it's properly closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db  # Provide the session to the endpoint
    finally:
        db.close()  # Always close the session, even if an error occurs
