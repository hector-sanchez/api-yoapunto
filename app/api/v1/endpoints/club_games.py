"""
Club Games Nested API Endpoints

This file defines the nested endpoints for managing the relationship between clubs and games.
These endpoints follow the pattern /clubs/{club_id}/games to manage which games a club plays.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.game import Game
from app.crud.club import get_club
from app.crud.game import get_game
from database import get_db

# Create router for nested club-games endpoints
router = APIRouter()

@router.get("/", response_model=List[Game])
def get_club_games(club_id: int, db: Session = Depends(get_db)):
    """
    Get all games that a specific club plays (HTTP GET)

    This endpoint returns all active games associated with the given club.
    Example: GET /clubs/123/games returns all games for club 123

    Args:
        club_id: ID of the club (from URL path)
        db: Database session (dependency injection)

    Returns:
        List[Game]: List of games this club plays

    Raises:
        HTTPException: 404 if club not found or inactive
    """
    # First verify the club exists and is active
    club = get_club(db=db, club_id=club_id)
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")

    # Return the games associated with this club
    # Filter to only include active games
    active_games = [game for game in club.games if game.active]
    return active_games

@router.post("/{game_id}")
def add_game_to_club(club_id: int, game_id: int, db: Session = Depends(get_db)):
    """
    Add a game to a club (HTTP POST)

    This creates an association between a club and a game, meaning the club
    now "plays" this game. Both the club and game must exist and be active.

    Args:
        club_id: ID of the club (from URL path)
        game_id: ID of the game to add (from URL path)
        db: Database session (dependency injection)

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 if club or game not found
        HTTPException: 400 if game already associated with club
    """
    # Verify both club and game exist and are active
    club = get_club(db=db, club_id=club_id)
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")

    game = get_game(db=db, game_id=game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if the game is already associated with this club
    if game in club.games:
        raise HTTPException(status_code=400, detail="Game already associated with this club")

    # Add the game to the club's games collection
    club.games.append(game)
    db.commit()

    return {"message": f"Game '{game.name}' successfully added to club '{club.nickname}'"}

@router.delete("/{game_id}")
def remove_game_from_club(club_id: int, game_id: int, db: Session = Depends(get_db)):
    """
    Remove a game from a club (HTTP DELETE)

    This removes the association between a club and a game. The game itself
    is not deleted, just the relationship is removed.

    Args:
        club_id: ID of the club (from URL path)
        game_id: ID of the game to remove (from URL path)
        db: Database session (dependency injection)

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 if club, game, or association not found
    """
    # Verify both club and game exist and are active
    club = get_club(db=db, club_id=club_id)
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")

    game = get_game(db=db, game_id=game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if the game is associated with this club
    if game not in club.games:
        raise HTTPException(status_code=404, detail="Game not associated with this club")

    # Remove the game from the club's games collection
    club.games.remove(game)
    db.commit()

    return {"message": f"Game '{game.name}' successfully removed from club '{club.nickname}'"}

@router.get("/{game_id}", response_model=Game)
def get_club_game(club_id: int, game_id: int, db: Session = Depends(get_db)):
    """
    Check if a specific game is associated with a club (HTTP GET)

    This endpoint verifies that a club plays a specific game and returns
    the game details if the association exists.

    Args:
        club_id: ID of the club (from URL path)
        game_id: ID of the game (from URL path)
        db: Database session (dependency injection)

    Returns:
        Game: The game details if associated with the club

    Raises:
        HTTPException: 404 if club, game, or association not found
    """
    # Verify the club exists and is active
    club = get_club(db=db, club_id=club_id)
    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")

    # Find the game in the club's games collection
    for game in club.games:
        if game.id == game_id and game.active:
            return game

    # Game not found in this club's games
    raise HTTPException(status_code=404, detail="Game not associated with this club or game not found")
