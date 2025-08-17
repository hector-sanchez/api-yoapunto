"""
JWT Authentication Utilities

This module handles JWT token creation, validation, and authentication dependencies
for the YoApunto API. It provides secure token-based authentication for user accounts.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db
from app.crud.account import get_account
from app.models.account import Account

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security schemes
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token

    Args:
        data: Dictionary of data to encode in the token (usually user ID and email)
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token to verify

    Returns:
        dict or None: Decoded token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Account:
    """
    Dependency to get the current authenticated account from JWT token

    This function extracts the JWT token from the Authorization header,
    verifies it, and returns the corresponding account from the database.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        Account: The authenticated account object

    Raises:
        HTTPException: 401 if token is invalid or account not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the token
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    # Extract account ID from token
    account_id: int = payload.get("sub")
    if account_id is None:
        raise credentials_exception

    # Get account from database
    account = get_account(db, account_id=int(account_id))
    if account is None:
        raise credentials_exception

    return account

def get_current_active_account(
    current_account: Account = Depends(get_current_account)
) -> Account:
    """
    Dependency to get the current authenticated and active account

    This ensures the account is not only authenticated but also active.

    Args:
        current_account: Current account from JWT token

    Returns:
        Account: The authenticated and active account

    Raises:
        HTTPException: 400 if account is inactive
    """
    if not current_account.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account"
        )
    return current_account

# Optional dependency for endpoints that work with or without authentication
def get_current_account_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Account]:
    """
    Optional dependency to get the current account if token is provided

    This allows endpoints to work both with and without authentication,
    providing different functionality based on authentication status.

    Args:
        credentials: Optional HTTP Bearer token
        db: Database session

    Returns:
        Account or None: Account if valid token provided, None otherwise
    """
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials)
    if payload is None:
        return None

    account_id = payload.get("sub")
    if account_id is None:
        return None

    return get_account(db, account_id=int(account_id))
