"""
Club CRUD Operations

CRUD stands for Create, Read, Update, Delete - the basic database operations.
This module contains all the business logic for working with clubs in the database.
These functions are called by the API endpoints to actually do the database work.
"""

from sqlalchemy.orm import Session
from app.models import Club
from app.schemas import ClubCreate, ClubUpdate

def create_club(db: Session, club: ClubCreate):
    """
    Create a new club in the database

    Args:
        db: Database session (connection to the database)
        club: ClubCreate schema with the new club data

    Returns:
        Club: The newly created club object from the database
    """
    # Convert Pydantic schema to dictionary, then create SQLAlchemy model
    # model_dump() converts the Pydantic object to a Python dict
    # **club.model_dump() unpacks the dict as keyword arguments
    db_club = Club(**club.model_dump())

    # Add the new club to the database session (like staging a change)
    db.add(db_club)

    # Commit the transaction (actually save the changes to the database)
    db.commit()

    # Refresh the object to get the auto-generated fields (id, timestamps)
    db.refresh(db_club)

    return db_club

def get_clubs(db: Session, skip: int = 0, limit: int = 100):
    """
    Get a list of active clubs with pagination

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List[Club]: List of active club objects
    """
    # Query the Club table, filter for active clubs only
    # This is where we implement "soft delete" - only show active clubs
    # offset() skips records, limit() limits how many we return
    return db.query(Club).filter(Club.active == True).offset(skip).limit(limit).all()

def get_club(db: Session, club_id: int):
    """
    Get a single club by its ID (only if it's active)

    Args:
        db: Database session
        club_id: The ID of the club to retrieve

    Returns:
        Club or None: The club object if found and active, None otherwise
    """
    # Filter by both ID and active status - this ensures deactivated clubs
    # can't be accessed even if someone knows their ID
    return db.query(Club).filter(Club.id == club_id, Club.active == True).first()

def update_club(db: Session, club_id: int, club: ClubUpdate):
    """
    Update an existing club

    Args:
        db: Database session
        club_id: ID of the club to update
        club: ClubUpdate schema with the new data

    Returns:
        Club or None: Updated club object if successful, None if club not found
    """
    # First, find the club to update (only if it's active)
    db_club = db.query(Club).filter(Club.id == club_id, Club.active == True).first()
    if db_club is None:
        return None  # Club not found or inactive

    # Get only the fields that were actually provided in the update
    # exclude_unset=True means only include fields that were explicitly set
    # This allows partial updates - users can update just nickname, or just thumbnail_url, etc.
    update_data = club.model_dump(exclude_unset=True)

    # Update each field that was provided
    # setattr() is Python's way of setting an attribute on an object
    for field, value in update_data.items():
        setattr(db_club, field, value)

    # Save the changes and refresh to get updated timestamps
    db.commit()
    db.refresh(db_club)
    return db_club

def deactivate_club(db: Session, club_id: int):
    """
    Deactivate a club (soft delete)

    Instead of actually deleting the club from the database, we just mark it
    as inactive. This preserves the data for audit purposes and allows for
    potential restoration later.

    Args:
        db: Database session
        club_id: ID of the club to deactivate

    Returns:
        Club or None: The deactivated club object if successful, None if not found
    """
    # Find the club (only if it's currently active)
    db_club = db.query(Club).filter(Club.id == club_id, Club.active == True).first()
    if db_club is None:
        return None  # Club not found or already inactive

    # Mark as inactive instead of deleting
    db_club.active = False

    # Save the change
    db.commit()
    return db_club
