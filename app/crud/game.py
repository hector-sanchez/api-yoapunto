"""
Game CRUD Operations

This module contains all the database operations for working with games.
These functions handle creating, reading, updating, and deactivating games.
"""

from sqlalchemy.orm import Session
from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdate

def create_game(db: Session, game: GameCreate):
    """
    Create a new game in the database

    Args:
        db: Database session
        game: GameCreate schema with the new game data

    Returns:
        Game: The newly created game object
    """
    # Convert Pydantic schema to SQLAlchemy model
    db_game = Game(**game.model_dump())

    # Add to database session and commit
    db.add(db_game)
    db.commit()
    db.refresh(db_game)  # Get auto-generated fields

    return db_game

def get_games(db: Session, skip: int = 0, limit: int = 100):
    """
    Get a list of active games with pagination

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List[Game]: List of active game objects
    """
    # Only return active games (soft delete implementation)
    return db.query(Game).filter(Game.active == True).offset(skip).limit(limit).all()

def get_game(db: Session, game_id: int):
    """
    Get a single game by its ID (only if active)

    Args:
        db: Database session
        game_id: The ID of the game to retrieve

    Returns:
        Game or None: The game object if found and active, None otherwise
    """
    return db.query(Game).filter(Game.id == game_id, Game.active == True).first()

def update_game(db: Session, game_id: int, game: GameUpdate):
    """
    Update an existing game

    Args:
        db: Database session
        game_id: ID of the game to update
        game: GameUpdate schema with the new data

    Returns:
        Game or None: Updated game object if successful, None if not found
    """
    # Find the game to update (only if active)
    db_game = db.query(Game).filter(Game.id == game_id, Game.active == True).first()
    if db_game is None:
        return None

    # Apply partial updates - only update fields that were provided
    update_data = game.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_game, field, value)

    # Save changes and refresh to get updated timestamp
    db.commit()
    db.refresh(db_game)
    return db_game

def deactivate_game(db: Session, game_id: int):
    """
    Deactivate a game (soft delete)

    Instead of deleting the game from the database, mark it as inactive.
    This preserves game data for historical records and potential restoration.

    Args:
        db: Database session
        game_id: ID of the game to deactivate

    Returns:
        Game or None: The deactivated game object if successful, None if not found
    """
    # Find the game (only if currently active)
    db_game = db.query(Game).filter(Game.id == game_id, Game.active == True).first()
    if db_game is None:
        return None

    # Mark as inactive instead of deleting
    db_game.active = False
    db.commit()
    return db_game
