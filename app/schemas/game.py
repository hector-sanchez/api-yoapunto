"""
Game Pydantic Schemas

These schemas define how game data should look when it comes into and goes out of our API.
They handle validation for game creation, updates, and responses.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Base schema with common game fields
class GameBase(BaseModel):
    """
    Base schema containing the core game fields used in multiple places
    """
    name: str = Field(..., min_length=1, max_length=100, description="Game name (1-100 characters)")
    description: Optional[str] = Field(None, max_length=500, description="Game description (up to 500 characters)")
    game_composition: str = Field(..., min_length=1, max_length=50, description="Game composition (e.g., 'player', 'team', 'player_or_team')")

    # Team limits - optional for games that don't use teams
    min_number_of_teams: Optional[int] = Field(None, ge=1, description="Minimum number of teams (must be >= 1 if specified)")
    max_number_of_teams: Optional[int] = Field(None, ge=1, description="Maximum number of teams (must be >= 1 if specified)")

    # Player limits - min is required, max is optional
    min_number_of_players: int = Field(..., ge=1, description="Minimum number of players (required, must be >= 1)")
    max_number_of_players: Optional[int] = Field(None, ge=1, description="Maximum number of players (must be >= 1 if specified)")

    # Players per team limits - for team-based games
    min_number_of_players_per_teams: Optional[int] = Field(None, ge=1, description="Minimum players per team (must be >= 1 if specified)")
    max_number_of_players_per_teams: Optional[int] = Field(None, ge=1, description="Maximum players per team (must be >= 1 if specified)")

    # Optional thumbnail image
    thumbnail: Optional[str] = Field(None, description="URL or path to game thumbnail image")

# Schema for creating new games
class GameCreate(GameBase):
    """
    Schema for creating new games via POST requests

    Inherits all fields from GameBase. No additional validation needed for creation.
    """
    pass

# Schema for updating existing games
class GameUpdate(BaseModel):
    """
    Schema for updating existing games via PUT requests

    All fields are optional to support partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Game name (1-100 characters)")
    description: Optional[str] = Field(None, max_length=500, description="Game description (up to 500 characters)")
    game_composition: Optional[str] = Field(None, min_length=1, max_length=50, description="Game composition")

    min_number_of_teams: Optional[int] = Field(None, ge=1, description="Minimum number of teams")
    max_number_of_teams: Optional[int] = Field(None, ge=1, description="Maximum number of teams")

    min_number_of_players: Optional[int] = Field(None, ge=1, description="Minimum number of players")
    max_number_of_players: Optional[int] = Field(None, ge=1, description="Maximum number of players")

    min_number_of_players_per_teams: Optional[int] = Field(None, ge=1, description="Minimum players per team")
    max_number_of_players_per_teams: Optional[int] = Field(None, ge=1, description="Maximum players per team")

    thumbnail: Optional[str] = Field(None, description="URL or path to game thumbnail image")
    active: Optional[bool] = Field(None, description="Whether the game is active")

# Schema for returning game data to clients
class Game(GameBase):
    """
    Schema for returning game data in API responses

    Includes all fields from GameBase plus auto-generated fields.
    """
    id: int  # Auto-generated primary key
    active: bool = True  # Show default value in API docs
    created_at: datetime  # Auto-generated creation timestamp
    updated_at: Optional[datetime] = None  # Auto-generated update timestamp

    class Config:
        """
        Pydantic configuration

        from_attributes=True allows creating this schema from SQLAlchemy model objects.
        """
        from_attributes = True

# Extended schema that includes the clubs relationship
# This is useful when you want to return a game with all clubs that play it
class GameWithClubs(Game):
    """
    Schema for returning game data with associated clubs

    This extends the basic Game schema to include the list of clubs
    that play this game. Useful for detailed game information.
    """
    clubs: List['Club'] = []  # List of clubs that play this game

    class Config:
        from_attributes = True

# Forward reference resolution for the clubs relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.club import Club
