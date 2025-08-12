"""
API Version 1 Router Configuration

This file brings together all the v1 API endpoints and organizes them
under a single router. This makes it easy to version your API - you could
later add a v2 folder with different endpoints while keeping v1 working.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import clubs

# Create the main API router for version 1
# This will collect all the individual endpoint routers
api_router = APIRouter()

# Include the clubs router with its specific configuration
# prefix="/clubs" means all club endpoints will be under /clubs/
# tags=["clubs"] groups these endpoints in the API documentation
# The final URLs will be: /api/v1/clubs/ (when included in main.py with /api/v1 prefix)
api_router.include_router(clubs.router, prefix="/clubs", tags=["clubs"])
