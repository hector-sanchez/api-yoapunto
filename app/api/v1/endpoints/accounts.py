"""
Account API Endpoints

Defines HTTP endpoints for common CRUD operations on accounts.
Accounts belong to clubs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.account import Account, AccountCreate, AccountUpdate, AccountPasswordUpdate, AccountWithClub
from app.crud.account import (
    create_account, get_accounts, get_account, get_account_by_email,
    get_club_accounts, update_account,
    update_account_password, deactivate_account
)
from app.crud.club import get_club  # Add this import
from database import get_db

# Create router for account endpoints
router = APIRouter()

@router.post("/", response_model=Account)
def create_account_endpoint(account: AccountCreate, db: Session = Depends(get_db)):
    """Create a new account"""
    try:
        # Check if email already exists
        existing_account = get_account_by_email(db, account.email_address)
        if existing_account:
            raise HTTPException(
                status_code=400,
                detail="Email address already registered"  # Fix: match test expectation
            )

        # Validate club exists if club_id is provided
        if account.club_id:
            existing_club = get_club(db, account.club_id)
            if not existing_club:
                raise HTTPException(
                    status_code=400,
                    detail="Club not found"
                )

        db_account = create_account(db=db, account=account)
        return db_account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Account])
def read_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get a list of accounts (HTTP GET)

    Returns active accounts with pagination support.

    Args:
        skip: Number of accounts to skip (query parameter)
        limit: Maximum number of accounts to return (query parameter)
        db: Database session (dependency injection)

    Returns:
        List[Account]: List of active accounts
    """
    return get_accounts(db=db, skip=skip, limit=limit)

@router.get("/{account_id}", response_model=AccountWithClub)
def read_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific account by ID (HTTP GET)

    Returns account information including associated club details.

    Args:
        account_id: ID of the account to retrieve (from URL path)
        db: Database session (dependency injection)

    Returns:
        AccountWithClub: The requested account with club information

    Raises:
        HTTPException: 404 if account not found or inactive
    """
    account = get_account(db=db, account_id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.get("/club/{club_id}", response_model=List[Account])
def read_club_accounts(
    club_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all accounts for a specific club (HTTP GET)

    Returns all active accounts that belong to the specified club.

    Args:
        club_id: ID of the club (from URL path)
        skip: Number of accounts to skip (query parameter)
        limit: Maximum number of accounts to return (query parameter)
        db: Database session (dependency injection)

    Returns:
        List[Account]: List of active accounts for the club

    Raises:
        HTTPException: 404 if club not found
    """
    # Verify club exists
    club = get_club(db=db, club_id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    return get_club_accounts(db=db, club_id=club_id, skip=skip, limit=limit)

@router.put("/{account_id}", response_model=Account)
def update_account_endpoint(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db)
):
    """Update an account"""
    try:
        # Check if email already exists (if being updated)
        if account_update.email_address:
            existing_account = get_account_by_email(
                db, account_update.email_address)
            if existing_account and existing_account.id != account_id:
                raise HTTPException(
                    status_code=400,
                    detail="Email address already registered"
                )

        # Validate club exists if club_id is being updated (only if field exists)
        if hasattr(account_update, 'club_id') and account_update.club_id:
            existing_club = get_club(db, account_update.club_id)
            if not existing_club:
                raise HTTPException(
                    status_code=400,
                    detail="Club not found"
                )

        db_account = update_account(
            db=db,
            account_id=account_id,
            account_update=account_update
        )
        if db_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return db_account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{account_id}/password", response_model=Account)
def update_account_password_endpoint(
    account_id: int,
    password_update: AccountPasswordUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an account's password by ID (HTTP PUT)

    Requires the current password for verification before setting the new password.
    The new password will be hashed before storing.

    Args:
        account_id: ID of the account to update (from URL path)
        password_update: AccountPasswordUpdate schema with current and new passwords
        db: Database session (dependency injection)

    Returns:
        Account: The updated account information

    Raises:
        HTTPException: 400 if current password is incorrect
    """
    updated_account = update_account_password(
        db=db,
        account_id=account_id,
        password_update=password_update
    )
    if updated_account is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    return updated_account

@router.delete("/{account_id}")
def delete_account_endpoint(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete (deactivate) an account by ID (HTTP DELETE)

    Implements soft delete - the account is marked as inactive rather than
    being permanently removed from the database.

    Args:
        account_id: ID of the account to deactivate (from URL path)
        db: Database session (dependency injection)

    Returns:
        dict: Success message
    """
    deactivate_account(db=db, account_id=account_id)
    return {"message": "Account deactivated successfully"}
