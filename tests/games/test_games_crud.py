"""
Game CRUD Tests

Unit tests for Game CRUD operations.
Tests database interactions and business logic for game operations.
"""

import pytest
from app.crud.game import create_game, get_games, get_game, update_game, deactivate_game
from app.schemas.game import GameCreate, GameUpdate

class TestGameCRUD:
    """Unit tests for Game CRUD operations"""

    def test_create_game_full(self, db):
        """Test creating a game with all fields through CRUD"""
        game_data = GameCreate(
            name="Basketball",
            description="Team sport with two teams of five players",
            game_composition="team",
            min_number_of_teams=2,
            max_number_of_teams=2,
            min_number_of_players=10,
            max_number_of_players=10,
            min_number_of_players_per_teams=5,
            max_number_of_players_per_teams=5,
            thumbnail="https://example.com/basketball.jpg"
        )

        game = create_game(db=db, game=game_data)

        assert game.id is not None
        assert game.name == "Basketball"
        assert game.description == "Team sport with two teams of five players"
        assert game.game_composition == "team"
        assert game.min_number_of_teams == 2
        assert game.max_number_of_teams == 2
        assert game.min_number_of_players == 10
        assert game.max_number_of_players == 10
        assert game.min_number_of_players_per_teams == 5
        assert game.max_number_of_players_per_teams == 5
        assert game.thumbnail == "https://example.com/basketball.jpg"
        assert game.active is True

    def test_create_game_minimal(self, db):
        """Test creating a game with only required fields"""
        game_data = GameCreate(
            name="Chess",
            game_composition="player",
            min_number_of_players=2
        )

        game = create_game(db=db, game=game_data)

        assert game.name == "Chess"
        assert game.game_composition == "player"
        assert game.min_number_of_players == 2
        assert game.description is None
        assert game.active is True

    def test_get_games_empty(self, db):
        """Test getting games from empty database"""
        games = get_games(db=db)
        assert games == []

    def test_get_games_with_data(self, db):
        """Test getting games with data"""
        # Create test games
        game1_data = GameCreate(name="Game 1", game_composition="player", min_number_of_players=1)
        game2_data = GameCreate(name="Game 2", game_composition="team", min_number_of_players=4)

        create_game(db=db, game=game1_data)
        create_game(db=db, game=game2_data)

        games = get_games(db=db)
        assert len(games) == 2
        assert games[0].name == "Game 1"
        assert games[1].name == "Game 2"

    def test_get_games_only_active(self, db):
        """Test that get_games only returns active games"""
        # Create active game
        active_game_data = GameCreate(name="Active Game", game_composition="player", min_number_of_players=1)
        active_game = create_game(db=db, game=active_game_data)

        # Create and deactivate a game
        inactive_game_data = GameCreate(name="Inactive Game", game_composition="player", min_number_of_players=1)
        inactive_game = create_game(db=db, game=inactive_game_data)
        deactivate_game(db=db, game_id=inactive_game.id)

        games = get_games(db=db)
        assert len(games) == 1
        assert games[0].name == "Active Game"

    def test_get_games_pagination(self, db):
        """Test pagination in get_games"""
        # Create 5 games
        for i in range(5):
            game_data = GameCreate(name=f"Game {i}", game_composition="player", min_number_of_players=1)
            create_game(db=db, game=game_data)

        # Test skip and limit
        games_page1 = get_games(db=db, skip=0, limit=2)
        games_page2 = get_games(db=db, skip=2, limit=2)

        assert len(games_page1) == 2
        assert len(games_page2) == 2
        assert games_page1[0].name != games_page2[0].name

    def test_get_game_by_id(self, db):
        """Test getting a specific game by ID"""
        game_data = GameCreate(name="Specific Game", game_composition="player", min_number_of_players=2)
        created_game = create_game(db=db, game=game_data)

        retrieved_game = get_game(db=db, game_id=created_game.id)

        assert retrieved_game is not None
        assert retrieved_game.id == created_game.id
        assert retrieved_game.name == "Specific Game"

    def test_get_game_nonexistent(self, db):
        """Test getting a game that doesn't exist"""
        game = get_game(db=db, game_id=999)
        assert game is None

    def test_get_game_inactive(self, db):
        """Test that get_game doesn't return inactive games"""
        game_data = GameCreate(name="Will Be Inactive", game_composition="player", min_number_of_players=1)
        created_game = create_game(db=db, game=game_data)

        # Deactivate the game
        deactivate_game(db=db, game_id=created_game.id)

        # Try to get the inactive game
        retrieved_game = get_game(db=db, game_id=created_game.id)
        assert retrieved_game is None

    def test_update_game(self, db):
        """Test updating a game"""
        game_data = GameCreate(name="Original Game", game_composition="player", min_number_of_players=2)
        created_game = create_game(db=db, game=game_data)

        update_data = GameUpdate(
            name="Updated Game",
            description="Updated description",
            max_number_of_players=8
        )
        updated_game = update_game(db=db, game_id=created_game.id, game=update_data)

        assert updated_game is not None
        assert updated_game.name == "Updated Game"
        assert updated_game.description == "Updated description"
        assert updated_game.game_composition == "player"  # Unchanged
        assert updated_game.max_number_of_players == 8

    def test_update_game_partial(self, db):
        """Test partial update of a game"""
        game_data = GameCreate(
            name="Partial Game",
            game_composition="team",
            min_number_of_players=6,
            min_number_of_teams=2
        )
        created_game = create_game(db=db, game=game_data)

        # Only update name
        update_data = GameUpdate(name="Partially Updated")
        updated_game = update_game(db=db, game_id=created_game.id, game=update_data)

        assert updated_game.name == "Partially Updated"
        assert updated_game.game_composition == "team"  # Unchanged
        assert updated_game.min_number_of_players == 6  # Unchanged

    def test_update_game_nonexistent(self, db):
        """Test updating a game that doesn't exist"""
        update_data = GameUpdate(name="Nonexistent")
        result = update_game(db=db, game_id=999, game=update_data)
        assert result is None

    def test_deactivate_game(self, db):
        """Test deactivating a game"""
        game_data = GameCreate(name="To Deactivate", game_composition="player", min_number_of_players=1)
        created_game = create_game(db=db, game=game_data)

        result = deactivate_game(db=db, game_id=created_game.id)

        assert result is not None
        assert result.active is False

        # Verify it's no longer returned by get_game
        retrieved_game = get_game(db=db, game_id=created_game.id)
        assert retrieved_game is None

    def test_deactivate_game_nonexistent(self, db):
        """Test deactivating a game that doesn't exist"""
        result = deactivate_game(db=db, game_id=999)
        assert result is None
