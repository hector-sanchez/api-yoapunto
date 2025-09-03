"""
Account Pydantic Schemas

These schemas define how account data should look when it comes into and goes out of our API.
They handle validation for account creation, updates, authentication, and responses.
Note: We never expose password_digest in API responses for security.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from .club import Club

# Base schema with common account fields (excludes sensitive data)
class AccountBase(BaseModel):
    """
    Base schema containing the core account fields that are safe to expose

    Note: This deliberately excludes password_digest for security reasons.
    """
    email_address: EmailStr = Field(..., description="Valid email address used for login")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name (1-100 characters)")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name (1-100 characters)")
    club_id: int = Field(..., description="ID of the club this account belongs to")

# Schema for creating new accounts
class AccountCreate(BaseModel):
    """
    Schema for creating new accounts via POST requests

    This includes the password field for account creation, but it gets
    hashed into password_digest before storing in the database.
    """
    email_address: EmailStr = Field(..., description="Valid email address used for login")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name (1-100 characters)")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name (1-100 characters)")
    password: str = Field(..., min_length=8, max_length=128, description="Password (8-128 characters, will be hashed)")
    club_id: int = Field(..., description="ID of the club this account belongs to")

# Schema for updating existing accounts
class AccountUpdate(BaseModel):
    """
    Schema for updating existing accounts via PUT requests

    All fields are optional to support partial updates.
    Password updates should be handled through a separate endpoint for security.
    """
    email_address: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    # Add this line if you want to allow club updates
    club_id: Optional[int] = None

# Schema for password changes (separate from general updates for security)
class AccountPasswordUpdate(BaseModel):
    """
    Schema specifically for password changes

    Requires both current and new password for security.
    """
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password (8-128 characters)")

# Schema for login requests
class AccountLogin(BaseModel):
    """
    Schema for authentication/login requests
    """
    email_address: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")

# Schema for token responses
class Token(BaseModel):
    """
    Schema for JWT token responses
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

# Schema for token data (what's encoded in the JWT)
class TokenData(BaseModel):
    """
    Schema for data stored in JWT tokens
    """
    account_id: Optional[int] = None
    email: Optional[str] = None

# Schema for returning account data to clients (excludes password_digest)
class Account(AccountBase):
    """
    Schema for returning account data in API responses

    This includes all safe fields but deliberately excludes password_digest
    and other sensitive authentication data.
    """
    id: int  # Auto-generated primary key
    active: bool = True  # Show default value in API docs
    email_verified: bool = False  # Email verification status
    last_login_at: Optional[datetime] = None  # Last login timestamp
    created_at: datetime  # Auto-generated creation timestamp
    updated_at: Optional[datetime] = None  # Auto-generated update timestamp

    class Config:
        """
        Pydantic configuration

        from_attributes=True allows creating this schema from SQLAlchemy model objects.
        """
        from_attributes = True

# Extended schema that includes the club relationship
class AccountWithClub(Account):
    """
    Schema for returning account data with associated club information

    Useful when you want to show account details along with club information.
    """
    club: Club

    class Config:
        from_attributes = True
