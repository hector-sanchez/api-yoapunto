"""
Account Database Model

This file defines the Account table structure using SQLAlchemy ORM.
The Account class represents user accounts that belong to clubs and are used for authentication.
Each account is associated with a specific club and contains authentication credentials.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Account(Base):
    """
    Account model - represents the 'accounts' table in the database

    This class defines user accounts that belong to clubs and handle authentication.
    Each account is linked to a specific club and contains login credentials.
    """

    # Tell SQLAlchemy what to name the table in the database
    __tablename__ = "accounts"

    # Primary key - unique identifier for each account
    id = Column(Integer, primary_key=True, index=True)

    # Email address - required field, must be unique across all accounts
    # This will be used as the username for authentication
    email_address = Column(String(255), nullable=False, unique=True, index=True)

    # User profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # Password digest - stores the hashed password (never store plain text passwords)
    # Using 'password_digest' name to make it clear this should contain hashed passwords
    password_digest = Column(String(255), nullable=False)

    # Foreign key to the clubs table - each account belongs to one club
    club_id = Column(Integer, ForeignKey('clubs.id'), nullable=False)

    # Account status - defaults to True (active)
    # Enables "soft delete" - we mark accounts as inactive instead of deleting them
    active = Column(Boolean, default=True, nullable=False)

    # Email verification status - track if the email has been verified
    email_verified = Column(Boolean, default=False, nullable=False)

    # Last login timestamp - track when the account was last used
    last_login_at = Column(DateTime(timezone=True))

    # Automatic timestamps for record creation and updates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to the Club model
    # This allows you to access account.club to get the club this account belongs to
    club = relationship("Club", back_populates="accounts")

    def __repr__(self):
        """String representation of the Account object"""
        return f"<Account(id={self.id}, email='{self.email_address}', name='{self.first_name} {self.last_name}')>"
