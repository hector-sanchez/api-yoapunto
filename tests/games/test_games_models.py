"""
Game Model Tests

Unit tests for the Game SQLAlchemy model.
Tests database model behavior, validation, and field constraints.
"""

import pytest
from datetime import datetime
from app.models.game import Game

class TestGameModel:
    """Unit tests for the Game model"""

    def test_game_creation_full(self, db):
        """Test creating a game with all fields"""
        game = Game(
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

        db.add(game)
        db.commit()
        db.refresh(game)

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
        assert isinstance(game.created_at, datetime)

    def test_game_creation_minimal(self, db):
        """Test creating a game with only required fields"""
        game = Game(
            name="Chess",
            game_composition="player",
            min_number_of_players=2
        )

        db.add(game)
        db.commit()
        db.refresh(game)

        assert game.name == "Chess"
        assert game.game_composition == "player"
        assert game.min_number_of_players == 2
        assert game.description is None
        assert game.min_number_of_teams is None
        assert game.max_number_of_teams is None
        assert game.max_number_of_players is None
        assert game.min_number_of_players_per_teams is None
        assert game.max_number_of_players_per_teams is None
        assert game.thumbnail is None
        assert game.active is True

    def test_game_active_default(self, db):
        """Test that active field defaults to True"""
        game = Game(
            name="Active Game",
            game_composition="player_or_team",
            min_number_of_players=1
        )

        db.add(game)
        db.commit()
        db.refresh(game)

        assert game.active is True

    def test_game_player_based_composition(self, db):
        """Test creating a player-based game"""
        game = Game(
            name="Solo Game",
            game_composition="player",
            min_number_of_players=1,
            max_number_of_players=8
        )

        db.add(game)
        db.commit()
        db.refresh(game)

        assert game.game_composition == "player"
        assert game.min_number_of_teams is None
        assert game.max_number_of_teams is None
        assert game.min_number_of_players_per_teams is None
        assert game.max_number_of_players_per_teams is None

    def test_game_team_based_composition(self, db):
        """Test creating a team-based game"""
        game = Game(
            name="Team Game",
            game_composition="team",
            min_number_of_teams=2,
            max_number_of_teams=4,
            min_number_of_players=6,
            max_number_of_players=20,
            min_number_of_players_per_teams=3,
            max_number_of_players_per_teams=5
        )

        db.add(game)
        db.commit()
        db.refresh(game)

        assert game.game_composition == "team"
        assert game.min_number_of_teams == 2
        assert game.max_number_of_teams == 4
        assert game.min_number_of_players_per_teams == 3
        assert game.max_number_of_players_per_teams == 5
