"""
Club-Games Association API Tests

Integration tests for the nested club-games endpoints.
Tests the many-to-many relationship between clubs and games through HTTP endpoints.
"""

from fastapi import status

class TestClubGamesAPI:
    """Integration tests for Club-Games association endpoints"""

    def test_get_club_games_empty(self, client):
        """Test getting games for a club that has no games"""
        # Create a club first
        club_data = {"nickname": "Empty Club", "creator": "empty_user"}
        create_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = create_response.json()

        # Get games for this club (should be empty)
        response = client.get(f"/api/v1/clubs/{created_club['id']}/games/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_club_games_not_found(self, client):
        """Test getting games for a club that doesn't exist"""
        response = client.get("/api/v1/clubs/999/games/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Club not found" in response.json()["detail"]

    def test_add_game_to_club_success(self, client):
        """Test successfully adding a game to a club"""
        # Create a club
        club_data = {"nickname": "Test Club", "creator": "test_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        # Create a game
        game_data = {
            "name": "Chess",
            "game_composition": "player",
            "min_number_of_players": 2
        }
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Add the game to the club
        response = client.post(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "successfully added" in data["message"]
        assert "Chess" in data["message"]
        assert "Test Club" in data["message"]

    def test_add_game_to_club_club_not_found(self, client):
        """Test adding a game to a club that doesn't exist"""
        # Create a game
        game_data = {
            "name": "Chess",
            "game_composition": "player",
            "min_number_of_players": 2
        }
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Try to add game to non-existent club
        response = client.post(f"/api/v1/clubs/999/games/{created_game['id']}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Club not found" in response.json()["detail"]

    def test_add_game_to_club_game_not_found(self, client):
        """Test adding a non-existent game to a club"""
        # Create a club
        club_data = {"nickname": "Test Club", "creator": "test_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        # Try to add non-existent game to club
        response = client.post(f"/api/v1/clubs/{created_club['id']}/games/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Game not found" in response.json()["detail"]

    def test_add_duplicate_game_to_club(self, client):
        """Test adding the same game to a club twice (should fail)"""
        # Create a club and game
        club_data = {"nickname": "Test Club", "creator": "test_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        game_data = {
            "name": "Chess",
            "game_composition": "player",
            "min_number_of_players": 2
        }
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Add the game to the club (first time - should succeed)
        response1 = client.post(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")
        assert response1.status_code == status.HTTP_200_OK

        # Try to add the same game again (should fail)
        response2 = client.post(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already associated" in response2.json()["detail"]

    def test_get_club_games_with_data(self, client):
        """Test getting games for a club that has games"""
        # Create a club
        club_data = {"nickname": "Gaming Club", "creator": "gamer_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        # Create multiple games
        game1_data = {"name": "Chess", "game_composition": "player", "min_number_of_players": 2}
        game2_data = {"name": "Basketball", "game_composition": "team", "min_number_of_players": 10}

        game1_response = client.post("/api/v1/games/", json=game1_data)
        game2_response = client.post("/api/v1/games/", json=game2_data)
        created_game1 = game1_response.json()
        created_game2 = game2_response.json()

        # Add both games to the club
        client.post(f"/api/v1/clubs/{created_club['id']}/games/{created_game1['id']}")
        client.post(f"/api/v1/clubs/{created_club['id']}/games/{created_game2['id']}")

        # Get all games for the club
        response = client.get(f"/api/v1/clubs/{created_club['id']}/games/")

        assert response.status_code == status.HTTP_200_OK
        games = response.json()
        assert len(games) == 2
        game_names = [game["name"] for game in games]
        assert "Chess" in game_names
        assert "Basketball" in game_names

    def test_get_specific_club_game_success(self, client):
        """Test getting a specific game for a club"""
        # Create club and game and associate them
        club_data = {"nickname": "Test Club", "creator": "test_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        game_data = {"name": "Chess", "game_composition": "player", "min_number_of_players": 2}
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Associate them
        client.post(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")

        # Get the specific game for this club
        response = client.get(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")

        assert response.status_code == status.HTTP_200_OK
        game = response.json()
        assert game["id"] == created_game["id"]
        assert game["name"] == "Chess"

    def test_get_specific_club_game_not_associated(self, client):
        """Test getting a game that's not associated with the club"""
        # Create club and game but don't associate them
        club_data = {"nickname": "Test Club", "creator": "test_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        game_data = {"name": "Chess", "game_composition": "player", "min_number_of_players": 2}
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Try to get the game for this club (not associated)
        response = client.get(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not associated" in response.json()["detail"]

    def test_remove_game_from_club_success(self, client):
        """Test successfully removing a game from a club"""
        # Create and associate club and game
        club_data = {"nickname": "Test Club", "creator": "test_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        game_data = {"name": "Chess", "game_composition": "player", "min_number_of_players": 2}
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Associate them
        client.post(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")

        # Remove the game from the club
        response = client.delete(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "successfully removed" in data["message"]
        assert "Chess" in data["message"]
        assert "Test Club" in data["message"]

        # Verify the game is no longer associated
        get_response = client.get(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_game_from_club_not_associated(self, client):
        """Test removing a game that's not associated with the club"""
        # Create club and game but don't associate them
        club_data = {"nickname": "Test Club", "creator": "test_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        game_data = {"name": "Chess", "game_composition": "player", "min_number_of_players": 2}
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Try to remove game that's not associated
        response = client.delete(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not associated" in response.json()["detail"]

    def test_remove_game_from_club_club_not_found(self, client):
        """Test removing a game from a club that doesn't exist"""
        # Create a game
        game_data = {"name": "Chess", "game_composition": "player", "min_number_of_players": 2}
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Try to remove from non-existent club
        response = client.delete(f"/api/v1/clubs/999/games/{created_game['id']}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Club not found" in response.json()["detail"]

    def test_club_games_only_shows_active_games(self, client):
        """Test that deactivated games don't appear in club's games list"""
        # Create club and game
        club_data = {"nickname": "Test Club", "creator": "test_user"}
        club_response = client.post("/api/v1/clubs/", json=club_data)
        created_club = club_response.json()

        game_data = {"name": "Chess", "game_composition": "player", "min_number_of_players": 2}
        game_response = client.post("/api/v1/games/", json=game_data)
        created_game = game_response.json()

        # Associate them
        client.post(f"/api/v1/clubs/{created_club['id']}/games/{created_game['id']}")

        # Verify game appears in club's games
        response = client.get(f"/api/v1/clubs/{created_club['id']}/games/")
        assert len(response.json()) == 1

        # Deactivate the game
        client.delete(f"/api/v1/games/{created_game['id']}")

        # Verify game no longer appears in club's games (even though association still exists)
        response = client.get(f"/api/v1/clubs/{created_club['id']}/games/")
        assert len(response.json()) == 0
