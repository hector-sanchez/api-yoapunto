"""
Club-Game Association Model

This file defines the many-to-many relationship between clubs and games.
A club can play multiple games, and a game can be played by multiple clubs.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Association table for many-to-many relationship between clubs and games
# This is a simple table that just links club IDs to game IDs
club_games = Table(
    'club_games',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('club_id', Integer, ForeignKey('clubs.id'), nullable=False),
    Column('game_id', Integer, ForeignKey('games.id'), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    # Ensure a club can't add the same game twice
    # UniqueConstraint would go here if you want to prevent duplicates
)
