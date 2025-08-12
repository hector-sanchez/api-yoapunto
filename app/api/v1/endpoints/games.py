"""
Game API Endpoints

This file defines the HTTP endpoints for game operations.
Games represent activities that clubs can organize with specific rules and participant limits.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.game import Game, GameCreate, GameUpdate
from app.crud.game import create_game, get_games, get_game, update_game, deactivate_game
from database import get_db

# Create router for game endpoints
router = APIRouter()

@router.post("/", response_model=Game)
def create_game_endpoint(game: GameCreate, db: Session = Depends(get_db)):
    """
    Create a new game (HTTP POST)

    Creates a new game with rules for participation limits and composition.
    All validation is handled automatically by Pydantic schemas.

    Args:
        game: GameCreate schema with game data from request JSON
        db: Database session (dependency injection)

    Returns:
        Game: The newly created game with all fields
    """
    return create_game(db=db, game=game)

@router.get("/", response_model=List[Game])
def read_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of games (HTTP GET)

    Returns active games with pagination support.
    Example: /games/?skip=10&limit=5 returns 5 games starting from the 11th

    Args:
        skip: Number of games to skip (query parameter)
        limit: Maximum number of games to return (query parameter)
        db: Database session (dependency injection)

    Returns:
        List[Game]: List of active games
    """
    return get_games(db=db, skip=skip, limit=limit)

@router.get("/{game_id}", response_model=Game)
def read_game(game_id: int, db: Session = Depends(get_db)):
    """
    Get a specific game by ID (HTTP GET)

    Example: GET /games/123 returns the game with ID 123

    Args:
        game_id: ID of the game to retrieve (from URL path)
        db: Database session (dependency injection)

    Returns:
        Game: The requested game

    Raises:
        HTTPException: 404 if game not found or inactive
    """
    game = get_game(db=db, game_id=game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.put("/{game_id}", response_model=Game)
def update_game_endpoint(game_id: int, game: GameUpdate, db: Session = Depends(get_db)):
    """
    Update an existing game (HTTP PUT)

    Supports partial updates - only include fields you want to change.
    For example, you can update just the description or just the player limits.

    Args:
        game_id: ID of game to update (from URL path)
        game: GameUpdate schema with new data (from request JSON)
        db: Database session (dependency injection)

    Returns:
        Game: The updated game with all current values

    Raises:
        HTTPException: 404 if game not found or inactive
    """
    updated_game = update_game(db=db, game_id=game_id, game=game)
    if updated_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return updated_game

@router.delete("/{game_id}")
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """
    Delete (deactivate) a game (HTTP DELETE)

    Implements soft delete - the game is marked as inactive rather than
    being permanently removed from the database.

    Args:
        game_id: ID of game to delete (from URL path)
        db: Database session (dependency injection)

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 if game not found or already inactive
    """
    game = deactivate_game(db=db, game_id=game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    return {"message": "Game deactivated successfully"}
