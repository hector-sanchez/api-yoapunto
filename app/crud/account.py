"""
Account CRUD Operations

This module handles all database operations for account management,
including creation, retrieval, updates, and soft deletion of user accounts.
"""

from datetime import datetime  # Add this import
from sqlalchemy.orm import Session
from sqlalchemy import and_
from passlib.context import CryptContext

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate, AccountPasswordUpdate

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password digest
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password digest from database

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_account(db: Session, account: AccountCreate):
    """
    Create a new account in the database

    Args:
        db: Database session
        account: AccountCreate schema with the new account data

    Returns:
        Account: The newly created account object
    """
    # Check if email already exists
    existing_account = get_account_by_email(db, account.email_address)
    if existing_account:
        raise ValueError("Email already registered")

    # Hash the password
    hashed_password = pwd_context.hash(account.password)

    # Create the account
    db_account = Account(
        email_address=account.email_address,
        password_digest=hashed_password,
        first_name=account.first_name,
        last_name=account.last_name,
        club_id=account.club_id,
        active=True
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    """
    Get a list of active accounts with pagination

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List[Account]: List of active account objects
    """
    # Only return active accounts (soft delete implementation)
    return db.query(Account).filter(Account.active == True).offset(skip).limit(limit).all()

def get_account(db: Session, account_id: int):
    """
    Get a single account by its ID (only if active)

    Args:
        db: Database session
        account_id: The ID of the account to retrieve

    Returns:
        Account or None: The account object if found and active, None otherwise
    """
    return db.query(Account).filter(
        and_(Account.id == account_id, Account.active == True)
    ).first()


def get_account_by_email(db: Session, email: str) -> Account | None:
    """
    Retrieve an account by email address.

    Args:
        db (Session): SQLAlchemy session
        email (str): Email address to search for

    Returns:
        Account or None: The account if found, else None
    """
    return db.query(Account).filter(Account.email_address == email).first()

def get_club_accounts(db: Session, club_id: int, skip: int = 0, limit: int = 100):
    """
    Get all accounts for a specific club

    Args:
        db: Database session
        club_id: ID of the club
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List[Account]: List of active accounts for the club
    """
    return db.query(Account).filter(
        and_(Account.club_id == club_id, Account.active == True)
    ).offset(skip).limit(limit).all()

def authenticate_account(db: Session, email_address: str, password: str):
    """
    Authenticate an account with email and password

    Args:
        db: Database session
        email_address: Email address for login
        password: Plain text password

    Returns:
        Account or None: Account object if authentication successful, None otherwise
    """
    # Get account by email
    account = get_account_by_email(db, email_address)
    if not account:
        return None

    # Verify password
    if not verify_password(password, account.password_digest):
        return None

    # Update last login timestamp
    account.last_login_at = datetime.utcnow()
    db.commit()

    return account


def update_account(db: Session, account_id: int, account_update: AccountUpdate):
    """Update an account with new data"""
    db_account = get_account(db, account_id)
    if not db_account:
        return None

    # Check for email conflicts if email is being updated
    if account_update.email_address and account_update.email_address != db_account.email_address:
        existing_account = get_account_by_email(
            db, account_update.email_address)
        if existing_account and existing_account.id != account_id:
            raise ValueError("Email already registered")

    # Update fields
    update_data = account_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_account, field, value)

    db_account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_account)
    return db_account

def update_account_password(db: Session, account_id: int, password_update: AccountPasswordUpdate):
    """
    Update an account's password after verifying the current password

    Args:
        db: Database session
        account_id: ID of the account to update
        password_update: AccountPasswordUpdate schema with current and new passwords

    Returns:
        Account or None: Updated account object if successful, None if not found or wrong password
    """
    # Find the account
    db_account = get_account(db, account_id)
    if db_account is None:
        return None

    # Verify current password
    if not verify_password(password_update.current_password, db_account.password_digest):
        return None

    # Hash and set new password
    db_account.password_digest = hash_password(password_update.new_password)

    # Save changes
    db.commit()
    db.refresh(db_account)
    return db_account

def deactivate_account(db: Session, account_id: int):
    """
    Deactivate an account (soft delete)

    Instead of deleting the account from the database, mark it as inactive.
    This preserves account data for audit purposes and prevents login.

    Args:
        db: Database session
        account_id: ID of the account to deactivate

    Returns:
        Account or None: The deactivated account object if successful, None if not found
    """
    # Find the account (only if currently active)
    db_account = get_account(db, account_id)
    if db_account is None:
        return None

    # Mark as inactive instead of deleting
    db_account.active = False
    db.commit()
    return db_account
