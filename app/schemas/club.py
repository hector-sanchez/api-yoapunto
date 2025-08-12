"""
Club Pydantic Schemas

These schemas define how data should look when it comes into and goes out of our API.
Pydantic automatically validates incoming data and converts outgoing data to JSON.
This is separate from the database model - schemas are for the API, models are for the database.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base schema with common fields
# Other schemas inherit from this to avoid repeating the same fields
class ClubBase(BaseModel):
    """
    Base schema containing the core club fields that are used in multiple places

    Field() allows us to add validation and documentation to each field:
    - ... means the field is required
    - min_length/max_length validate string length
    - description appears in the API documentation
    """
    nickname: str = Field(..., min_length=1, max_length=50, description="Club nickname (1-50 characters)")
    creator: str = Field(..., min_length=1, max_length=50, description="Club creator name (1-50 characters)")
    thumbnail_url: Optional[str] = Field(None, description="URL to club thumbnail image")

# Schema for creating new clubs
# Inherits all fields from ClubBase, no additional fields needed
class ClubCreate(ClubBase):
    """
    Schema for creating new clubs via POST requests

    This inherits all the fields from ClubBase. We don't need id, timestamps,
    or active status when creating - those are handled automatically.
    """
    pass

# Schema for updating existing clubs
# All fields are optional since users might only want to update some fields
class ClubUpdate(BaseModel):
    """
    Schema for updating existing clubs via PUT requests

    All fields are Optional because users might only want to update
    some fields (partial updates). The CRUD layer handles which fields
    actually get updated.
    """
    nickname: Optional[str] = Field(None, min_length=1, max_length=50, description="Club nickname (1-50 characters)")
    creator: Optional[str] = Field(None, min_length=1, max_length=50, description="Club creator name (1-50 characters)")
    thumbnail_url: Optional[str] = Field(None, description="URL to club thumbnail image")
    active: Optional[bool] = Field(None, description="Whether the club is active")

# Schema for returning club data to clients
# Includes all fields, including the auto-generated ones like id and timestamps
class Club(ClubBase):
    """
    Schema for returning club data in API responses

    This includes all the fields from ClubBase plus the fields that are
    automatically generated (id, active status, timestamps).
    """
    id: int  # Auto-generated primary key
    active: bool = True  # Show default value in API docs
    created_at: datetime  # Auto-generated creation timestamp
    updated_at: Optional[datetime] = None  # Auto-generated update timestamp (None until first update)

    class Config:
        """
        Pydantic configuration for this schema

        from_attributes=True tells Pydantic it can create this schema
        from SQLAlchemy model objects (which have attributes, not dict keys).
        This is what allows us to return database objects from our API endpoints.
        """
        from_attributes = True
