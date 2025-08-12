"""
Game Database Model

This file defines the Game table structure using SQLAlchemy ORM.
The Game class represents how game data is stored in the database.
Games define the rules and structure for activities that clubs can organize.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class Game(Base):
    """
    Game model - represents the 'games' table in the database

    This class defines the structure for games that clubs can play.
    Each game has composition rules (player/team based) and participant limits.
    """

    # Tell SQLAlchemy what to name the table in the database
    __tablename__ = "games"

    # Primary key - unique identifier for each game
    id = Column(Integer, primary_key=True, index=True)

    # Game name - required field
    # index=True because we'll often search games by name
    name = Column(String(100), nullable=False, index=True)

    # Game description - optional detailed explanation
    description = Column(String(500))

    # Game composition - defines how the game is structured
    # Examples: "player", "team", "player_or_team"
    # This determines whether individuals or teams participate
    game_composition = Column(String(50), nullable=False)

    # Team limits - minimum and maximum number of teams that can participate
    # These can be None if the game doesn't use teams
    min_number_of_teams = Column(Integer)
    max_number_of_teams = Column(Integer)

    # Player limits - minimum and maximum total number of players
    min_number_of_players = Column(Integer, nullable=False)
    max_number_of_players = Column(Integer)

    # Players per team limits - for team-based games
    # These define how many players each team should have
    min_number_of_players_per_teams = Column(Integer)
    max_number_of_players_per_teams = Column(Integer)

    # Optional URL or path to the game's thumbnail image
    thumbnail = Column(String)

    # Active status - defaults to True (active)
    # Enables "soft delete" - we mark games as inactive instead of deleting them
    active = Column(Boolean, default=True, nullable=False)

    # Automatic timestamps for record creation and updates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
