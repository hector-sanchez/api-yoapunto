from fastapi import status

class TestClubAPI:
    """Integration tests for Club API endpoints"""

    def test_create_club_success(self, client):
        """Test successful club creation via API"""
        club_data = {
            "nickname": "API Test Club",
            "creator": "api_user",
            "thumbnail_url": "https://example.com/api.jpg"
        }

        response = client.post("/api/v1/clubs/", json=club_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nickname"] == "API Test Club"
        assert data["creator"] == "api_user"
        assert data["thumbnail_url"] == "https://example.com/api.jpg"
        assert data["active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_club_without_thumbnail(self, client):
        """Test creating club without thumbnail URL"""
        club_data = {
            "nickname": "No Thumbnail Club",
            "creator": "no_thumb_user"
        }

        response = client.post("/api/v1/clubs/", json=club_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["thumbnail_url"] is None

    def test_create_club_validation_errors(self, client):
        """Test validation errors in club creation"""
        # Test missing required fields
        response = client.post("/api/v1/clubs/", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test empty nickname
        club_data = {"nickname": "", "creator": "user"}
        response = client.post("/api/v1/clubs/", json=club_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test nickname too long
        club_data = {"nickname": "a" * 51, "creator": "user"}
        response = client.post("/api/v1/clubs/", json=club_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test creator too long
        club_data = {"nickname": "club", "creator": "b" * 51}
        response = client.post("/api/v1/clubs/", json=club_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_clubs_empty(self, client):
        """Test getting clubs from empty database"""
        response = client.get("/api/v1/clubs/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_clubs_with_data(self, client):
        """Test getting clubs with data"""
        # Create test clubs
        club1_data = {"nickname": "Club 1", "creator": "user1"}
        club2_data = {"nickname": "Club 2", "creator": "user2"}

        client.post("/api/v1/clubs/", json=club1_data)
        client.post("/api/v1/clubs/", json=club2_data)

        response = client.get("/api/v1/clubs/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["nickname"] == "Club 1"
        assert data[1]["nickname"] == "Club 2"

    def test_get_clubs_pagination(self, client):
        """Test clubs pagination"""
        # Create 5 clubs
        for i in range(5):
            club_data = {"nickname": f"Club {i}", "creator": f"user{i}"}
            client.post("/api/v1/clubs/", json=club_data)

        # Test pagination
        response = client.get("/api/v1/clubs/?skip=0&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

        response = client.get("/api/v1/clubs/?skip=2&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_club_by_id(self, client):
        """Test getting a specific club by ID"""
        club_data = {"nickname": "Specific Club", "creator": "specific_user"}
        create_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = create_response.json()

        response = client.get(f"/api/v1/clubs/{created_club['id']}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created_club["id"]
        assert data["nickname"] == "Specific Club"

    def test_get_club_not_found(self, client):
        """Test getting a club that doesn't exist"""
        response = client.get("/api/v1/clubs/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Club not found" in response.json()["detail"]

    def test_update_club_success(self, client):
        """Test successful club update"""
        # Create a club first
        club_data = {"nickname": "Original Club", "creator": "original_user"}
        create_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = create_response.json()

        # Update the club
        update_data = {
            "nickname": "Updated Club",
            "thumbnail_url": "https://example.com/updated.jpg"
        }
        response = client.put(f"/api/v1/clubs/{created_club['id']}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nickname"] == "Updated Club"
        assert data["creator"] == "original_user"  # Unchanged
        assert data["thumbnail_url"] == "https://example.com/updated.jpg"

    def test_update_club_partial(self, client):
        """Test partial club update"""
        # Create a club first
        club_data = {"nickname": "Partial Club", "creator": "partial_user"}
        create_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = create_response.json()

        # Partial update - only nickname
        update_data = {"nickname": "Partially Updated"}
        response = client.put(f"/api/v1/clubs/{created_club['id']}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nickname"] == "Partially Updated"
        assert data["creator"] == "partial_user"

    def test_update_club_validation_errors(self, client):
        """Test validation errors in club update"""
        # Create a club first
        club_data = {"nickname": "Valid Club", "creator": "valid_user"}
        create_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = create_response.json()

        # Test empty nickname
        update_data = {"nickname": ""}
        response = client.put(f"/api/v1/clubs/{created_club['id']}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test nickname too long
        update_data = {"nickname": "a" * 51}
        response = client.put(f"/api/v1/clubs/{created_club['id']}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_club_not_found(self, client):
        """Test updating a club that doesn't exist"""
        update_data = {"nickname": "Nonexistent"}
        response = client.put("/api/v1/clubs/999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_club_success(self, client):
        """Test successful club deletion (deactivation)"""
        # Create a club first
        club_data = {"nickname": "To Delete", "creator": "delete_user"}
        create_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = create_response.json()

        # Delete the club
        response = client.delete(f"/api/v1/clubs/{created_club['id']}")

        assert response.status_code == status.HTTP_200_OK
        assert "deactivated successfully" in response.json()["message"]

        # Verify club is no longer accessible
        get_response = client.get(f"/api/v1/clubs/{created_club['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_club_not_found(self, client):
        """Test deleting a club that doesn't exist"""
        response = client.delete("/api/v1/clubs/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_club_removes_from_list(self, client):
        """Test that deleted clubs don't appear in club list"""
        # Create two clubs
        club1_data = {"nickname": "Keep Club", "creator": "keep_user"}
        club2_data = {"nickname": "Delete Club", "creator": "delete_user"}

        create_response1 = client.post("/api/v1/clubs/", json=club1_data)
        create_response2 = client.post("/api/v1/clubs/", json=club2_data)

        created_club2 = create_response2.json()

        # Verify both clubs are in the list
        response = client.get("/api/v1/clubs/")
        assert len(response.json()) == 2

        # Delete one club
        client.delete(f"/api/v1/clubs/{created_club2['id']}")

        # Verify only one club remains in the list
        response = client.get("/api/v1/clubs/")
        data = response.json()
        assert len(data) == 1
        assert data[0]["nickname"] == "Keep Club"

    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        assert "Welcome to YoApunto API" in response.json()["message"]
