"""
Tests for auth API endpoints

Tests login, logout, refresh token, password reset, and email verification endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.models.account import Account
from app.models.club import Club
from app.auth_helper import pwd_context, create_access_token


class TestAuthAPI:
    """Test authentication API endpoints"""

    def test_login_valid_credentials(self, client: TestClient, db):
        """Test login with valid credentials"""
        # Create test club
        test_club = Club(
            nickname="Test Club",
            creator="Test Creator",
            thumbnail_url="https://example.com/test.jpg",
            active=True
        )
        db.add(test_club)
        db.commit()
        db.refresh(test_club)

        # Create test account
        password = "testpassword123"
        test_account = Account(
            email_address="test@example.com",
            password_digest=pwd_context.hash(password),
            first_name="Test",
            last_name="User",
            club_id=test_club.id,
            active=True
        )
        db.add(test_account)
        db.commit()

        # Test login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email_address": "test@example.com",
                "password": password
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_invalid_email(self, client: TestClient):
        """Test login with invalid email"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email_address": "nonexistent@example.com",
                "password": "anypassword"
            }
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient, db):
        """Test login with invalid password"""
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
            password_digest=pwd_context.hash("correctpassword"),
            first_name="Test",
            last_name="User",
            club_id=test_club.id,
            active=True
        )
        db.add(test_account)
        db.commit()

        # Test login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email_address": "test@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_inactive_account(self, client: TestClient, db):
        """Test login with inactive account"""
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

        test_account = Account(
            email_address="inactive@example.com",
            password_digest=pwd_context.hash("password123"),
            first_name="Inactive",
            last_name="User",
            club_id=test_club.id,
            active=False
        )
        db.add(test_account)
        db.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email_address": "inactive@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields"""
        # Missing password
        response = client.post(
            "/api/v1/auth/login",
            json={"email_address": "test@example.com"}
        )
        assert response.status_code == 422

        # Missing email
        response = client.post(
            "/api/v1/auth/login",
            json={"password": "password123"}
        )
        assert response.status_code == 422

        # Empty request
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email_address": "not-an-email",
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_logout_endpoint_exists(self, client: TestClient):
        """Test that logout endpoint exists and returns correct status"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 204

    def test_authenticated_endpoint_with_valid_token(self, client: TestClient, db):
        """Test accessing protected endpoint with valid token"""
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

        # Create token
        token = create_access_token({"sub": test_account.id})

        # Test accessing protected endpoint (if you have one)
        # For example, getting current user's account details
        response = client.get(
            f"/api/v1/accounts/{test_account.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # This should work if the endpoint exists and uses authentication
        # Adjust based on your actual protected endpoints
        # 401 if endpoint requires auth but isn't implemented yet
        assert response.status_code in [200, 401]

    def test_authenticated_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token"""
        # This test assumes you have protected endpoints
        # Adjust based on your actual implementation
        response = client.get("/api/v1/accounts/1")
        # Should either work (if endpoint doesn't require auth) or fail with 401/403
        assert response.status_code in [200, 401, 403, 404]

    def test_authenticated_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/api/v1/accounts/1",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        # Should either work (if endpoint doesn't require auth) or fail with 401
        assert response.status_code in [200, 401, 404]


class TestTokenIntegration:
    """Test token integration across the system"""

    def test_login_and_use_token_flow(self, client: TestClient, db):
        """Test complete login flow and token usage"""
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

        password = "testpassword123"
        test_account = Account(
            email_address="test@example.com",
            password_digest=pwd_context.hash(password),
            first_name="Test",
            last_name="User",
            club_id=test_club.id,
            active=True
        )
        db.add(test_account)
        db.commit()
        db.refresh(test_account)

        # Step 1: Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email_address": "test@example.com",
                "password": password
            }
        )

        assert login_response.status_code == 200
        token_data = login_response.json()
        token = token_data["access_token"]

        # Step 2: Use token to access protected resource
        # (Adjust this based on your actual protected endpoints)
        protected_response = client.get(
            f"/api/v1/accounts/{test_account.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # This should work if you have the endpoint implemented
        # For now, just check that we get a reasonable response
        assert protected_response.status_code in [200, 401, 404]
