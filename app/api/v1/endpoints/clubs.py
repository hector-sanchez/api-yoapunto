"""
Club API Endpoints

This file defines the HTTP endpoints (URLs) that clients can call to interact with clubs.
Each function here handles a specific HTTP request (GET, POST, PUT, DELETE) and
returns the appropriate HTTP response.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import Club, ClubCreate, ClubUpdate
from app.crud.club import create_club, get_clubs, get_club, update_club, deactivate_club
from database import get_db

# Create an APIRouter - this groups related endpoints together
# This router will be included in the main app with a prefix like /api/v1/clubs
router = APIRouter()

@router.post("/", response_model=Club)
def create_club_endpoint(club: ClubCreate, db: Session = Depends(get_db)):
    """
    Create a new club (HTTP POST)

    This endpoint accepts JSON data matching the ClubCreate schema,
    validates it automatically thanks to Pydantic, then creates the club
    in the database.

    Args:
        club: ClubCreate schema automatically parsed from request JSON
        db: Database session injected by FastAPI using the get_db dependency

    Returns:
        Club: The newly created club with all fields (including auto-generated ones)
    """
    # Call the CRUD function to do the actual database work
    # The separation of concerns: endpoints handle HTTP, CRUD handles database
    return create_club(db=db, club=club)

@router.get("/", response_model=List[Club])
def read_clubs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of clubs (HTTP GET)

    This endpoint supports pagination through query parameters:
    - /clubs/ returns first 100 clubs
    - /clubs/?skip=10&limit=5 returns 5 clubs starting from the 11th

    Args:
        skip: Number of clubs to skip (query parameter, defaults to 0)
        limit: Maximum number of clubs to return (query parameter, defaults to 100)
        db: Database session (dependency injection)

    Returns:
        List[Club]: List of active clubs
    """
    return get_clubs(db=db, skip=skip, limit=limit)

@router.get("/{club_id}", response_model=Club)
def read_club(club_id: int, db: Session = Depends(get_db)):
    """
    Get a specific club by ID (HTTP GET)

    The {club_id} in the path becomes a parameter to this function.
    For example: GET /clubs/123 will call this function with club_id=123

    Args:
        club_id: ID of the club to retrieve (from URL path)
        db: Database session (dependency injection)

    Returns:
        Club: The requested club

    Raises:
        HTTPException: 404 error if club not found or inactive
    """
    club = get_club(db=db, club_id=club_id)
    if club is None:
        # HTTPException is FastAPI's way of returning HTTP error responses
        # This will return a 404 Not Found with a JSON error message
        raise HTTPException(status_code=404, detail="Club not found")
    return club

@router.put("/{club_id}", response_model=Club)
def update_club_endpoint(club_id: int, club: ClubUpdate, db: Session = Depends(get_db)):
    """
    Update an existing club (HTTP PUT)

    This endpoint supports partial updates - you only need to include the fields
    you want to change in the JSON request body.

    Args:
        club_id: ID of club to update (from URL path)
        club: ClubUpdate schema with new data (from request JSON)
        db: Database session (dependency injection)

    Returns:
        Club: The updated club with all current field values

    Raises:
        HTTPException: 404 error if club not found or inactive
    """
    updated_club = update_club(db=db, club_id=club_id, club=club)
    if updated_club is None:
        raise HTTPException(status_code=404, detail="Club not found")
    return updated_club

@router.delete("/{club_id}")
def delete_club(club_id: int, db: Session = Depends(get_db)):
    """
    Delete (deactivate) a club (HTTP DELETE)

    This implements "soft delete" - the club isn't actually removed from the database,
    just marked as inactive. This preserves data for audit purposes.

    Args:
        club_id: ID of club to delete (from URL path)
        db: Database session (dependency injection)

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 error if club not found or already inactive
    """
    club = deactivate_club(db=db, club_id=club_id)
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")

    # Return a simple success message instead of the club data
    # This is a common pattern for DELETE endpoints
    return {"message": "Club deactivated successfully"}
