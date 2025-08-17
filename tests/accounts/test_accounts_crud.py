# tests/accounts/test_accounts_crud.py
"""
Tests for account CRUD operations

Tests all database operations for accounts including
creation, querying, updating, and soft deletion.
"""

import pytest
from sqlalchemy.orm import Session
from app.models.account import Account
from app.models.club import Club
from app.crud.account import (
    create_account, get_accounts, get_account, get_account_by_email,
    get_club_accounts, update_account, update_account_password, deactivate_account
)
from app.crud.club import create_club
from app.schemas.account import AccountCreate, AccountUpdate, AccountPasswordUpdate
from app.schemas.club import ClubCreate


class TestAccountCRUD:
    """Test class for account CRUD operations"""

    def test_create_account(self, db):
        """Test creating a new account"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        account_data = AccountCreate(
            email_address="test@example.com",
            password="testpassword123",
            first_name="John",
            last_name="Doe",
            club_id=test_club.id
        )

        account = create_account(db=db, account=account_data)

        assert account.id is not None
        assert account.email_address == "test@example.com"
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.club_id == test_club.id
        assert account.active is True
        assert account.password_digest is not None
        assert account.password_digest != "testpassword123"  # Should be hashed
        assert account.created_at is not None
        assert account.updated_at is None  # Should be None for newly created records

    def test_get_accounts(self, db):
        """Test getting list of accounts"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test accounts
        accounts = []
        for i in range(5):
            account = create_account(
                db=db,
                account=AccountCreate(
                    email_address=f"test{i}@example.com",
                    password="testpassword123",
                    first_name=f"User{i}",
                    last_name="Test",
                    club_id=test_club.id
                )
            )
            accounts.append(account)

        # Deactivate one account to test filtering
        deactivate_account(db=db, account_id=accounts[0].id)

        # Get active accounts
        result = get_accounts(db=db)

        assert len(result) == 4  # Only active accounts
        assert all(account.active for account in result)

    def test_get_accounts_pagination(self, db):
        """Test getting accounts with pagination"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test accounts
        for i in range(10):
            create_account(
                db=db,
                account=AccountCreate(
                    email_address=f"page{i}@example.com",
                    password="testpassword123",
                    first_name=f"Page{i}",
                    last_name="Test",
                    club_id=test_club.id
                )
            )

        # Test pagination
        page1 = get_accounts(db=db, skip=0, limit=3)
        page2 = get_accounts(db=db, skip=3, limit=3)

        assert len(page1) == 3
        assert len(page2) == 3
        assert page1[0].id != page2[0].id  # Different accounts

    def test_get_account(self, db):
        """Test getting a single account by ID"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test account
        test_account = create_account(
            db=db,
            account=AccountCreate(
                email_address="single@example.com",
                password="testpassword123",
                first_name="Single",
                last_name="Test",
                club_id=test_club.id
            )
        )

        # Get the account
        result = get_account(db=db, account_id=test_account.id)

        assert result is not None
        assert result.id == test_account.id
        assert result.email_address == "single@example.com"

    def test_get_account_not_found(self, db):
        """Test getting non-existent account"""
        result = get_account(db=db, account_id=99999)
        assert result is None

    def test_get_account_inactive(self, db):
        """Test getting deactivated account returns None"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create and deactivate account
        test_account = create_account(
            db=db,
            account=AccountCreate(
                email_address="inactive@example.com",
                password="testpassword123",
                first_name="Inactive",
                last_name="Test",
                club_id=test_club.id
            )
        )

        deactivate_account(db=db, account_id=test_account.id)

        # Try to get deactivated account
        result = get_account(db=db, account_id=test_account.id)
        assert result is None

    def test_get_account_by_email(self, db):
        """Test getting account by email address"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test account
        test_account = create_account(
            db=db,
            account=AccountCreate(
                email_address="email@example.com",
                password="testpassword123",
                first_name="Email",
                last_name="Test",
                club_id=test_club.id
            )
        )

        # Get by email
        result = get_account_by_email(db=db, email_address="email@example.com")

        assert result is not None
        assert result.id == test_account.id
        assert result.email_address == "email@example.com"

    def test_get_account_by_email_not_found(self, db):
        """Test getting account by non-existent email"""
        result = get_account_by_email(db=db, email_address="notfound@example.com")
        assert result is None

    def test_get_club_accounts(self, db):
        """Test getting accounts for a specific club"""
        # Create test clubs
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        club2 = create_club(
            db=db,
            club=ClubCreate(
                name="Second Club",
                nickname="second_club",
                description="Another club",
                address="456 Test Ave",
                creator="test_creator2"
            )
        )

        # Create accounts for both clubs
        for i in range(3):
            create_account(
                db=db,
                account=AccountCreate(
                    email_address=f"club1_{i}@example.com",
                    password="testpassword123",
                    first_name=f"Club1User{i}",
                    last_name="Test",
                    club_id=test_club.id
                )
            )

        for i in range(2):
            create_account(
                db=db,
                account=AccountCreate(
                    email_address=f"club2_{i}@example.com",
                    password="testpassword123",
                    first_name=f"Club2User{i}",
                    last_name="Test",
                    club_id=club2.id
                )
            )

        # Get accounts for first club
        club1_accounts = get_club_accounts(db=db, club_id=test_club.id)
        assert len(club1_accounts) == 3
        assert all(account.club_id == test_club.id for account in club1_accounts)

        # Get accounts for second club
        club2_accounts = get_club_accounts(db=db, club_id=club2.id)
        assert len(club2_accounts) == 2
        assert all(account.club_id == club2.id for account in club2_accounts)

    def test_update_account(self, db):
        """Test updating an account"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test account
        test_account = create_account(
            db=db,
            account=AccountCreate(
                email_address="update@example.com",
                password="testpassword123",
                first_name="Original",
                last_name="Name",
                club_id=test_club.id
            )
        )

        # Update account
        update_data = AccountUpdate(
            first_name="Updated",
            last_name="Name",
            email_address="updated@example.com"
        )

        updated_account = update_account(
            db=db,
            account_id=test_account.id,
            account=update_data
        )

        assert updated_account is not None
        assert updated_account.first_name == "Updated"
        assert updated_account.last_name == "Name"
        assert updated_account.email_address == "updated@example.com"
        assert updated_account.updated_at >= updated_account.created_at

    def test_update_account_partial(self, db):
        """Test partial account update"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test account
        test_account = create_account(
            db=db,
            account=AccountCreate(
                email_address="partial@example.com",
                password="testpassword123",
                first_name="Partial",
                last_name="Update",
                club_id=test_club.id
            )
        )

        # Update only first name
        update_data = AccountUpdate(first_name="PartialUpdated")

        updated_account = update_account(
            db=db,
            account_id=test_account.id,
            account=update_data
        )

        assert updated_account.first_name == "PartialUpdated"
        assert updated_account.last_name == "Update"  # Unchanged
        assert updated_account.email_address == "partial@example.com"  # Unchanged

    def test_update_account_not_found(self, db):
        """Test updating non-existent account"""
        update_data = AccountUpdate(first_name="NotFound")

        result = update_account(
            db=db,
            account_id=99999,
            account=update_data
        )

        assert result is None

    def test_update_account_password(self, db):
        """Test updating account password"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test account
        test_account = create_account(
            db=db,
            account=AccountCreate(
                email_address="password@example.com",
                password="oldpassword123",
                first_name="Password",
                last_name="Test",
                club_id=test_club.id
            )
        )

        original_digest = test_account.password_digest

        # Update password
        password_update = AccountPasswordUpdate(
            current_password="oldpassword123",
            new_password="newpassword123"
        )

        updated_account = update_account_password(
            db=db,
            account_id=test_account.id,
            password_update=password_update
        )

        assert updated_account is not None
        assert updated_account.password_digest != original_digest
        assert updated_account.password_digest != "newpassword123"  # Should be hashed

    def test_update_account_password_wrong_current(self, db):
        """Test updating password with wrong current password"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test account
        test_account = create_account(
            db=db,
            account=AccountCreate(
                email_address="wrongpass@example.com",
                password="correctpassword123",
                first_name="Wrong",
                last_name="Pass",
                club_id=test_club.id
            )
        )

        # Try with wrong current password
        password_update = AccountPasswordUpdate(
            current_password="wrongpassword123",
            new_password="newpassword123"
        )

        result = update_account_password(
            db=db,
            account_id=test_account.id,
            password_update=password_update
        )

        assert result is None

    def test_deactivate_account(self, db):
        """Test deactivating an account (soft delete)"""
        # Create a test club for account associations
        test_club = create_club(
            db=db,
            club=ClubCreate(
                name="Test Club",
                nickname="test_club",
                description="Club for testing",
                address="123 Test St",
                creator="test_creator"
            )
        )

        # Create test account
        test_account = create_account(
            db=db,
            account=AccountCreate(
                email_address="deactivate@example.com",
                password="testpassword123",
                first_name="Deactivate",
                last_name="Test",
                club_id=test_club.id
            )
        )

        assert test_account.active is True

        # Deactivate account
        deactivated = deactivate_account(db=db, account_id=test_account.id)

        assert deactivated is not None
        assert deactivated.active is False

        # Verify account is no longer returned by normal queries
        result = get_account(db=db, account_id=test_account.id)
        assert result is None

    def test_deactivate_account_not_found(self, db):
        """Test deactivating non-existent account"""
        result = deactivate_account(db=db, account_id=99999)
        assert result is None
