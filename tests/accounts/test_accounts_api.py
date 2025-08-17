# tests/accounts/test_accounts_api.py
"""
Tests for account API endpoints

Tests all the REST endpoints for account operations including
creation, reading, updating, and deletion.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from app.models.account import Account
from app.models.club import Club
from app.crud.account import create_account
from app.crud.club import create_club
from app.schemas.account import AccountCreate
from app.schemas.club import ClubCreate
from conftest import TestingSessionLocal


class TestAccountAPI:
    """Test class for account API endpoints"""

    def test_create_account_success(self, client):
        """Test successful account creation"""
        # First create a club for the account
        club_data = {
            "nickname": "Test Club",
            "creator": "Test Creator",
            "thumbnail_url": "https://example.com/thumbnail.jpg"
        }
        club_response = client.post("/api/v1/clubs/", json=club_data)
        assert club_response.status_code == 200
        club = club_response.json()

        account_data = {
            "email_address": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe",
            "club_id": club["id"]
        }

        response = client.post("/api/v1/accounts/", json=account_data)

        assert response.status_code == 200
        data = response.json()
        assert data["email_address"] == "test@example.com"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["club_id"] == club["id"]
        assert data["active"] is True
        assert "password_digest" not in data  # Password should not be returned

    def test_create_account_duplicate_email(self, client):
        """Test account creation with duplicate email"""
        # First create a club for the accounts
        club_data = {
            "nickname": "Test Club",
            "creator": "Test Creator"
        }
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create first account
        account_data = {
            "email_address": "duplicate@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe",
            "club_id": club["id"]
        }

        response1 = client.post("/api/v1/accounts/", json=account_data)
        assert response1.status_code == 200

        # Try to create second account with same email
        response2 = client.post("/api/v1/accounts/", json=account_data)
        assert response2.status_code == 400
        assert "Email address already registered" in response2.json()["detail"]

    def test_create_account_invalid_club(self, client):
        """Test account creation with non-existent club"""
        account_data = {
            "email_address": "test@example.com",
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe",
            "club_id": 99999  # Non-existent club ID
        }

        response = client.post("/api/v1/accounts/", json=account_data)
        assert response.status_code == 400
        assert "Club not found" in response.json()["detail"]

    def test_read_accounts(self, client):
        """Test getting list of accounts"""
        # First create a club
        club_data = {"nickname": "Test Club", "creator": "Test Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create test accounts
        for i in range(3):
            account_data = {
                "email_address": f"test{i}@example.com",
                "password": "testpassword123",
                "first_name": f"User{i}",
                "last_name": "Test",
                "club_id": club["id"]
            }
            client.post("/api/v1/accounts/", json=account_data)

        response = client.get("/api/v1/accounts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert all(account["active"] for account in data)

    def test_read_accounts_pagination(self, client):
        """Test accounts pagination"""
        # First create a club
        club_data = {"nickname": "Page Club", "creator": "Page Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create test accounts
        for i in range(5):
            account_data = {
                "email_address": f"page{i}@example.com",
                "password": "testpassword123",
                "first_name": f"Page{i}",
                "last_name": "Test",
                "club_id": club["id"]
            }
            client.post("/api/v1/accounts/", json=account_data)

        # Test with limit
        response = client.get("/api/v1/accounts/?skip=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_read_account_by_id(self, client):
        """Test getting a specific account by ID"""
        # First create a club
        club_data = {"nickname": "Specific Club", "creator": "Specific Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create test account
        account_data = {
            "email_address": "specific@example.com",
            "password": "testpassword123",
            "first_name": "Specific",
            "last_name": "User",
            "club_id": club["id"]
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        account = account_response.json()

        response = client.get(f"/api/v1/accounts/{account['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account["id"]
        assert data["email_address"] == "specific@example.com"
        assert "club" in data  # Should include club information

    def test_read_account_not_found(self, client):
        """Test getting non-existent account"""
        response = client.get("/api/v1/accounts/99999")
        assert response.status_code == 404
        assert "Account not found" in response.json()["detail"]

    def test_read_club_accounts(self, client):
        """Test getting accounts for a specific club"""
        # First create a club
        club_data = {"nickname": "Club Accounts", "creator": "Club Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create accounts for the test club
        for i in range(3):
            account_data = {
                "email_address": f"club{i}@example.com",
                "password": "testpassword123",
                "first_name": f"ClubUser{i}",
                "last_name": "Test",
                "club_id": club["id"]
            }
            client.post("/api/v1/accounts/", json=account_data)

        response = client.get(f"/api/v1/accounts/club/{club['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert all(account["club_id"] == club["id"] for account in data)

    def test_read_club_accounts_not_found(self, client):
        """Test getting accounts for non-existent club"""
        response = client.get("/api/v1/accounts/club/99999")
        assert response.status_code == 404
        assert "Club not found" in response.json()["detail"]

    def test_update_account(self, client):
        """Test updating an account"""
        # First create a club
        club_data = {"nickname": "Update Club", "creator": "Update Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create test account
        account_data = {
            "email_address": "update@example.com",
            "password": "testpassword123",
            "first_name": "Update",
            "last_name": "Test",
            "club_id": club["id"]
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        account = account_response.json()

        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }

        response = client.put(f"/api/v1/accounts/{account['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["email_address"] == "update@example.com"  # Unchanged

    def test_update_account_duplicate_email(self, client):
        """Test updating account with duplicate email"""
        # First create a club
        club_data = {"nickname": "Duplicate Club", "creator": "Duplicate Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create two accounts
        account1_data = {
            "email_address": "first@example.com",
            "password": "testpassword123",
            "first_name": "First",
            "last_name": "User",
            "club_id": club["id"]
        }
        account1_response = client.post("/api/v1/accounts/", json=account1_data)

        account2_data = {
            "email_address": "second@example.com",
            "password": "testpassword123",
            "first_name": "Second",
            "last_name": "User",
            "club_id": club["id"]
        }
        account2_response = client.post("/api/v1/accounts/", json=account2_data)
        account2 = account2_response.json()

        # Try to update second account with first account's email
        update_data = {"email_address": "first@example.com"}
        response = client.put(f"/api/v1/accounts/{account2['id']}", json=update_data)
        assert response.status_code == 400
        assert "Email address already registered" in response.json()["detail"]

    def test_update_account_not_found(self, client):
        """Test updating non-existent account"""
        update_data = {"first_name": "Updated"}
        response = client.put("/api/v1/accounts/99999", json=update_data)
        assert response.status_code == 404
        assert "Account not found" in response.json()["detail"]

    def test_update_account_password(self, client):
        """Test updating account password"""
        # First create a club
        club_data = {"nickname": "Password Club", "creator": "Password Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create test account
        account_data = {
            "email_address": "password@example.com",
            "password": "oldpassword123",
            "first_name": "Password",
            "last_name": "Test",
            "club_id": club["id"]
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        account = account_response.json()

        password_data = {
            "current_password": "oldpassword123",
            "new_password": "newpassword123"
        }

        response = client.put(f"/api/v1/accounts/{account['id']}/password", json=password_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account["id"]

    def test_update_account_password_wrong_current(self, client):
        """Test updating password with wrong current password"""
        # First create a club
        club_data = {"nickname": "Wrong Pass Club", "creator": "Wrong Pass Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create test account
        account_data = {
            "email_address": "wrongpass@example.com",
            "password": "correctpassword123",
            "first_name": "Wrong",
            "last_name": "Pass",
            "club_id": club["id"]
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        account = account_response.json()

        password_data = {
            "current_password": "wrongpassword123",
            "new_password": "newpassword123"
        }

        response = client.put(f"/api/v1/accounts/{account['id']}/password", json=password_data)
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

    def test_delete_account(self, client):
        """Test deleting (deactivating) an account"""
        # First create a club
        club_data = {"nickname": "Delete Club", "creator": "Delete Creator"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        club = club_response.json()

        # Create test account
        account_data = {
            "email_address": "delete@example.com",
            "password": "testpassword123",
            "first_name": "Delete",
            "last_name": "Test",
            "club_id": club["id"]
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        account = account_response.json()

        response = client.delete(f"/api/v1/accounts/{account['id']}")
        assert response.status_code == 200
        assert "Account deactivated successfully" in response.json()["message"]

        # Verify account is no longer accessible
        get_response = client.get(f"/api/v1/accounts/{account['id']}")
        assert get_response.status_code == 404
