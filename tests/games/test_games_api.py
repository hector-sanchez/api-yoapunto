"""
Game API Tests

Integration tests for Game API endpoints.
Tests HTTP endpoints, status codes, and request/response handling for games.
"""

from fastapi import status

class TestGameAPI:
    """Integration tests for Game API endpoints"""

    def test_create_game_success(self, client):
        """Test successful game creation via API"""
        game_data = {
            "name": "Basketball",
            "description": "Team sport with two teams of five players",
            "game_composition": "team",
            "min_number_of_teams": 2,
            "max_number_of_teams": 2,
            "min_number_of_players": 10,
            "max_number_of_players": 10,
            "min_number_of_players_per_teams": 5,
            "max_number_of_players_per_teams": 5,
            "thumbnail": "https://example.com/basketball.jpg"
        }

        response = client.post("/api/v1/games/", json=game_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Basketball"
        assert data["description"] == "Team sport with two teams of five players"
        assert data["game_composition"] == "team"
        assert data["min_number_of_teams"] == 2
        assert data["max_number_of_teams"] == 2
        assert data["min_number_of_players"] == 10
        assert data["max_number_of_players"] == 10
        assert data["min_number_of_players_per_teams"] == 5
        assert data["max_number_of_players_per_teams"] == 5
        assert data["thumbnail"] == "https://example.com/basketball.jpg"
        assert data["active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_game_minimal(self, client):
        """Test creating game with only required fields"""
        game_data = {
            "name": "Chess",
            "game_composition": "player",
            "min_number_of_players": 2
        }

        response = client.post("/api/v1/games/", json=game_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Chess"
        assert data["game_composition"] == "player"
        assert data["min_number_of_players"] == 2
        assert data["description"] is None
        assert data["min_number_of_teams"] is None

    def test_create_game_validation_errors(self, client):
        """Test validation errors in game creation"""
        # Test missing required fields
        response = client.post("/api/v1/games/", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test empty name
        game_data = {"name": "", "game_composition": "player", "min_number_of_players": 1}
        response = client.post("/api/v1/games/", json=game_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test name too long
        game_data = {
            "name": "a" * 101,
            "game_composition": "player",
            "min_number_of_players": 1
        }
        response = client.post("/api/v1/games/", json=game_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test invalid min_number_of_players (must be >= 1)
        game_data = {
            "name": "Invalid Game",
            "game_composition": "player",
            "min_number_of_players": 0
        }
        response = client.post("/api/v1/games/", json=game_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_games_empty(self, client):
        """Test getting games from empty database"""
        response = client.get("/api/v1/games/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_games_with_data(self, client):
        """Test getting games with data"""
        # Create test games
        game1_data = {"name": "Game 1", "game_composition": "player", "min_number_of_players": 1}
        game2_data = {"name": "Game 2", "game_composition": "team", "min_number_of_players": 4}

        client.post("/api/v1/games/", json=game1_data)
        client.post("/api/v1/games/", json=game2_data)

        response = client.get("/api/v1/games/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Game 1"
        assert data[1]["name"] == "Game 2"

    def test_get_games_pagination(self, client):
        """Test games pagination"""
        # Create 5 games
        for i in range(5):
            game_data = {
                "name": f"Game {i}",
                "game_composition": "player",
                "min_number_of_players": 1
            }
            client.post("/api/v1/games/", json=game_data)

        # Test pagination
        response = client.get("/api/v1/games/?skip=0&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

        response = client.get("/api/v1/games/?skip=2&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_game_by_id(self, client):
        """Test getting a specific game by ID"""
        game_data = {
            "name": "Specific Game",
            "game_composition": "player",
            "min_number_of_players": 2
        }
        create_response = client.post("/api/v1/games/", json=game_data)
        created_game = create_response.json()

        response = client.get(f"/api/v1/games/{created_game['id']}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created_game["id"]
        assert data["name"] == "Specific Game"

    def test_get_game_not_found(self, client):
        """Test getting a game that doesn't exist"""
        response = client.get("/api/v1/games/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Game not found" in response.json()["detail"]

    def test_update_game_success(self, client):
        """Test successful game update"""
        # Create a game first
        game_data = {
            "name": "Original Game",
            "game_composition": "player",
            "min_number_of_players": 2
        }
        create_response = client.post("/api/v1/games/", json=game_data)
        created_game = create_response.json()

        # Update the game
        update_data = {
            "name": "Updated Game",
            "description": "Updated description",
            "max_number_of_players": 8
        }
        response = client.put(f"/api/v1/games/{created_game['id']}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Game"
        assert data["description"] == "Updated description"
        assert data["game_composition"] == "player"  # Unchanged
        assert data["max_number_of_players"] == 8

    def test_update_game_partial(self, client):
        """Test partial game update"""
        # Create a game first
        game_data = {
            "name": "Partial Game",
            "game_composition": "team",
            "min_number_of_players": 6
        }
        create_response = client.post("/api/v1/games/", json=game_data)
        created_game = create_response.json()

        # Partial update - only name
        update_data = {"name": "Partially Updated"}
        response = client.put(f"/api/v1/games/{created_game['id']}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Partially Updated"
        assert data["game_composition"] == "team"  # Unchanged

    def test_update_game_validation_errors(self, client):
        """Test validation errors in game update"""
        # Create a game first
        game_data = {
            "name": "Valid Game",
            "game_composition": "player",
            "min_number_of_players": 2
        }
        create_response = client.post("/api/v1/games/", json=game_data)
        created_game = create_response.json()

        # Test empty name
        update_data = {"name": ""}
        response = client.put(f"/api/v1/games/{created_game['id']}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test name too long
        update_data = {"name": "a" * 101}
        response = client.put(f"/api/v1/games/{created_game['id']}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_game_not_found(self, client):
        """Test updating a game that doesn't exist"""
        update_data = {"name": "Nonexistent"}
        response = client.put("/api/v1/games/999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_game_success(self, client):
        """Test successful game deletion (deactivation)"""
        # Create a game first
        game_data = {
            "name": "To Delete",
            "game_composition": "player",
            "min_number_of_players": 1
        }
        create_response = client.post("/api/v1/games/", json=game_data)
        created_game = create_response.json()

        # Delete the game
        response = client.delete(f"/api/v1/games/{created_game['id']}")

        assert response.status_code == status.HTTP_200_OK
        assert "deactivated successfully" in response.json()["message"]

        # Verify game is no longer accessible
        get_response = client.get(f"/api/v1/games/{created_game['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_game_not_found(self, client):
        """Test deleting a game that doesn't exist"""
        response = client.delete("/api/v1/games/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_root_endpoint(self, client):
        """Test the root endpoint still works"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        assert "Welcome to YoApunto API" in response.json()["message"]
