"""
YoApunto API - Main Application Entry Point

This is the main FastAPI application file that ties everything together.
It sets up the database, includes API routes, and configures the web server.
"""

from fastapi import FastAPI
from app.api.v1.api import api_router
from database import engine, Base
# Import models to register them with Base - this is important!
# Without this import, SQLAlchemy won't know about our Club, Game, and Account models
from app.models import club, game, account

# Create all database tables on startup
# This line tells SQLAlchemy to create any missing tables in the database
Base.metadata.create_all(bind=engine)

# Create the FastAPI application instance
# title and version will appear in the auto-generated API documentation
app = FastAPI(title="YoApunto API", version="1.0.0")

@app.get("/")
def read_root():
    """
    Root endpoint - a simple health check for the API
    This will return a welcome message when someone visits the base URL
    """
    return {"message": "Welcome to YoApunto API"}

# Include API routes with versioning
# All club-related endpoints will be available under /api/v1/clubs/
app.include_router(api_router, prefix="/api/v1")
