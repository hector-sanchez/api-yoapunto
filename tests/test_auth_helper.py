"""
Tests for auth_helper module

Tests JWT token creation, verification, and authentication dependencies.
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock

from app.auth_helper import (
    create_access_token,
    verify_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_account,
    get_current_active_account,
    get_current_account_optional,
    SECRET_KEY,
    ALGORITHM,
    pwd_context
)
from app.models.account import Account
from app.models.club import Club


class TestTokenCreation:
    """Test token creation and verification"""

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry"""
        data = {"sub": 1, "email": "test@example.com"}
        token = create_access_token(data)

        # Verify token can be decoded
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "1"  # JWT converts to string
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": 1}
        custom_expiry = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_expiry)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "1"  # JWT converts to string

        # Check expiry is approximately 60 minutes from now
        exp_time = datetime.utcfromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + custom_expiry
        assert abs((exp_time - expected_time).total_seconds()) < 5

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": 1}
        token = create_refresh_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "1"  # JWT converts to string

        # Check expiry is approximately 7 days from now
        exp_time = datetime.utcfromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + timedelta(days=7)
        assert abs((exp_time - expected_time).total_seconds()) < 60

    def test_verify_token_valid(self):
        """Test verifying valid token"""
        data = {"sub": 1, "email": "test@example.com"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "1"  # JWT converts to string
        assert payload["email"] == "test@example.com"

    def test_verify_refresh_token_valid(self):
        """Test verifying valid refresh token"""
        data = {"sub": 1}
        token = create_refresh_token(data)

        payload = verify_refresh_token(token)
        assert payload is not None
        assert payload["sub"] == "1"  # JWT converts to string

    def test_verify_token_invalid(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        assert payload is None

    def test_verify_token_expired(self):
        """Test verifying expired token"""
        data = {"sub": 1}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        payload = verify_token(token)
        assert payload is None

    def test_verify_refresh_token_invalid(self):
        """Test verifying invalid refresh token"""
        payload = verify_refresh_token("invalid.token")
        assert payload is None


class TestPasswordHashing:
    """Test password hashing utilities"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = pwd_context.hash(password)

        # Verify correct password
        assert pwd_context.verify(password, hashed) is True

        # Verify incorrect password
        assert pwd_context.verify("wrongpassword", hashed) is False

    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes"""
        password = "testpassword123"
        hash1 = pwd_context.hash(password)
        hash2 = pwd_context.hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify correctly
        assert pwd_context.verify(password, hash1) is True
        assert pwd_context.verify(password, hash2) is True


class TestAuthDependencies:
    """Test authentication dependencies"""

    def test_get_current_account_valid_token(self, db):
        """Test getting current account with valid token"""
        # Create test club and account
        test_club = Club(
            nickname="Test Club",
            creator="Test Creator",
            thumbnail_url="https://example.com/test.jpg",
            active=True
        )
        db.add(test_club)
        db.commit()
        db.refresh(test_club)

        test_account = Account(
            email_address="test@example.com",
            password_digest=pwd_context.hash("password123"),
            first_name="Test",
            last_name="User",
            club_id=test_club.id,
            active=True
        )
        db.add(test_account)
        db.commit()
        db.refresh(test_account)

        # Create token for account
        token = create_access_token({"sub": test_account.id})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token)

        # Test dependency
        account = get_current_account(credentials, db)
        assert account.id == test_account.id
        assert account.email_address == "test@example.com"

    def test_get_current_account_invalid_token(self, db):
        """Test getting current account with invalid token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token")

        with pytest.raises(HTTPException) as exc_info:
            get_current_account(credentials, db)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    def test_get_current_account_nonexistent_user(self, db):
        """Test getting current account for nonexistent user"""
        # Create token for nonexistent user
        token = create_access_token({"sub": 99999})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            get_current_account(credentials, db)

        assert exc_info.value.status_code == 401

    def test_get_current_active_account_active_user(self, db):
        """Test getting current active account with active user"""
        # Create test club and active account
        test_club = Club(
            nickname="Test Club",
            creator="Test Creator",
            thumbnail_url="https://example.com/test.jpg",
            active=True
        )
        db.add(test_club)
        db.commit()
        db.refresh(test_club)

        active_account = Account(
            email_address="active@example.com",
            password_digest=pwd_context.hash("password123"),
            first_name="Active",
            last_name="User",
            club_id=test_club.id,
            active=True
        )
        db.add(active_account)
        db.commit()

        account = get_current_active_account(active_account)
        assert account == active_account

    def test_get_current_active_account_inactive_user(self, db):
        """Test getting current active account with inactive user"""
        # Create test club and inactive account
        test_club = Club(
            nickname="Test Club",
            creator="Test Creator",
            thumbnail_url="https://example.com/test.jpg",
            active=True
        )
        db.add(test_club)
        db.commit()
        db.refresh(test_club)

        inactive_account = Account(
            email_address="inactive@example.com",
            password_digest=pwd_context.hash("password123"),
            first_name="Inactive",
            last_name="User",
            club_id=test_club.id,
            active=False
        )
        db.add(inactive_account)
        db.commit()

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_account(inactive_account)

        assert exc_info.value.status_code == 400
        assert "Inactive account" in exc_info.value.detail

    def test_get_current_account_optional_with_token(self, db):
        """Test optional account dependency with valid token"""
        # Create test club and account
        test_club = Club(
            nickname="Test Club",
            creator="Test Creator",
            thumbnail_url="https://example.com/test.jpg",
            active=True
        )
        db.add(test_club)
        db.commit()
        db.refresh(test_club)

        test_account = Account(
            email_address="test@example.com",
            password_digest=pwd_context.hash("password123"),
            first_name="Test",
            last_name="User",
            club_id=test_club.id,
            active=True
        )
        db.add(test_account)
        db.commit()
        db.refresh(test_account)

        token = create_access_token({"sub": test_account.id})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token)

        account = get_current_account_optional(credentials, db)
        assert account is not None
        assert account.id == test_account.id

    def test_get_current_account_optional_no_token(self, db):
        """Test optional account dependency without token"""
        account = get_current_account_optional(None, db)
        assert account is None

    def test_get_current_account_optional_invalid_token(self, db):
        """Test optional account dependency with invalid token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token")
        account = get_current_account_optional(credentials, db)
        assert account is None
