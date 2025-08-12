"""
Club Database Model

This file defines the Club table structure using SQLAlchemy ORM.
The Club class represents how club data is stored in the database.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class Club(Base):
    """
    Club model - represents the 'clubs' table in the database

    This class inherits from Base, which tells SQLAlchemy this is a database model.
    Each attribute becomes a column in the database table.
    """

    # Tell SQLAlchemy what to name the table in the database
    __tablename__ = "clubs"

    # Primary key - unique identifier for each club
    # index=True creates a database index for faster lookups
    id = Column(Integer, primary_key=True, index=True)

    # Club nickname - required field with maximum 50 characters
    # nullable=False means this field cannot be empty
    # index=True because we'll often search by nickname
    nickname = Column(String(50), nullable=False, index=True)

    # Creator name - required field with maximum 50 characters
    creator = Column(String(50), nullable=False)

    # Optional URL for the club's thumbnail image
    # No length limit specified, so it can be any length
    thumbnail_url = Column(String)

    # Active status - defaults to True (active)
    # This enables "soft delete" - we mark clubs as inactive instead of deleting them
    active = Column(Boolean, default=True, nullable=False)

    # Automatic timestamp when the record is created
    # server_default means the database sets this value automatically
    # func.now() is SQLAlchemy's way of saying "current timestamp"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Automatic timestamp when the record is updated
    # onupdate means this gets updated every time the record changes
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
