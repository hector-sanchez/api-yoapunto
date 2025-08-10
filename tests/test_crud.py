import pytest
from app.crud.club import create_club, get_clubs, get_club, update_club, deactivate_club
from app.schemas import ClubCreate, ClubUpdate

class TestClubCRUD:
    """Unit tests for Club CRUD operations"""

    def test_create_club(self, db):
        """Test creating a club through CRUD"""
        club_data = ClubCreate(
            nickname="CRUD Test Club",
            creator="crud_user",
            thumbnail_url="https://example.com/crud.jpg"
        )

        club = create_club(db=db, club=club_data)

        assert club.id is not None
        assert club.nickname == "CRUD Test Club"
        assert club.creator == "crud_user"
        assert club.thumbnail_url == "https://example.com/crud.jpg"
        assert club.active is True

    def test_create_club_without_thumbnail(self, db):
        """Test creating a club without thumbnail URL"""
        club_data = ClubCreate(nickname="No Thumb Club", creator="no_thumb_user")

        club = create_club(db=db, club=club_data)

        assert club.thumbnail_url is None
        assert club.active is True

    def test_get_clubs_empty(self, db):
        """Test getting clubs from empty database"""
        clubs = get_clubs(db=db)
        assert clubs == []

    def test_get_clubs_with_data(self, db):
        """Test getting clubs with data"""
        # Create test clubs
        club1_data = ClubCreate(nickname="Club 1", creator="user1")
        club2_data = ClubCreate(nickname="Club 2", creator="user2")

        create_club(db=db, club=club1_data)
        create_club(db=db, club=club2_data)

        clubs = get_clubs(db=db)
        assert len(clubs) == 2
        assert clubs[0].nickname == "Club 1"
        assert clubs[1].nickname == "Club 2"

    def test_get_clubs_only_active(self, db):
        """Test that get_clubs only returns active clubs"""
        # Create active club
        active_club_data = ClubCreate(nickname="Active Club", creator="active_user")
        active_club = create_club(db=db, club=active_club_data)

        # Create and deactivate a club
        inactive_club_data = ClubCreate(nickname="Inactive Club", creator="inactive_user")
        inactive_club = create_club(db=db, club=inactive_club_data)
        deactivate_club(db=db, club_id=inactive_club.id)

        clubs = get_clubs(db=db)
        assert len(clubs) == 1
        assert clubs[0].nickname == "Active Club"

    def test_get_clubs_pagination(self, db):
        """Test pagination in get_clubs"""
        # Create 5 clubs
        for i in range(5):
            club_data = ClubCreate(nickname=f"Club {i}", creator=f"user{i}")
            create_club(db=db, club=club_data)

        # Test skip and limit
        clubs_page1 = get_clubs(db=db, skip=0, limit=2)
        clubs_page2 = get_clubs(db=db, skip=2, limit=2)

        assert len(clubs_page1) == 2
        assert len(clubs_page2) == 2
        assert clubs_page1[0].nickname != clubs_page2[0].nickname

    def test_get_club_by_id(self, db):
        """Test getting a specific club by ID"""
        club_data = ClubCreate(nickname="Specific Club", creator="specific_user")
        created_club = create_club(db=db, club=club_data)

        retrieved_club = get_club(db=db, club_id=created_club.id)

        assert retrieved_club is not None
        assert retrieved_club.id == created_club.id
        assert retrieved_club.nickname == "Specific Club"

    def test_get_club_nonexistent(self, db):
        """Test getting a club that doesn't exist"""
        club = get_club(db=db, club_id=999)
        assert club is None

    def test_get_club_inactive(self, db):
        """Test that get_club doesn't return inactive clubs"""
        club_data = ClubCreate(nickname="Will Be Inactive", creator="inactive_user")
        created_club = create_club(db=db, club=club_data)

        # Deactivate the club
        deactivate_club(db=db, club_id=created_club.id)

        # Try to get the inactive club
        retrieved_club = get_club(db=db, club_id=created_club.id)
        assert retrieved_club is None

    def test_update_club(self, db):
        """Test updating a club"""
        club_data = ClubCreate(nickname="Original Club", creator="original_user")
        created_club = create_club(db=db, club=club_data)

        update_data = ClubUpdate(nickname="Updated Club", thumbnail_url="https://example.com/updated.jpg")
        updated_club = update_club(db=db, club_id=created_club.id, club=update_data)

        assert updated_club is not None
        assert updated_club.nickname == "Updated Club"
        assert updated_club.creator == "original_user"  # Unchanged
        assert updated_club.thumbnail_url == "https://example.com/updated.jpg"

    def test_update_club_partial(self, db):
        """Test partial update of a club"""
        club_data = ClubCreate(nickname="Partial Club", creator="partial_user")
        created_club = create_club(db=db, club=club_data)

        # Only update nickname
        update_data = ClubUpdate(nickname="Partially Updated")
        updated_club = update_club(db=db, club_id=created_club.id, club=update_data)

        assert updated_club.nickname == "Partially Updated"
        assert updated_club.creator == "partial_user"  # Unchanged

    def test_update_club_nonexistent(self, db):
        """Test updating a club that doesn't exist"""
        update_data = ClubUpdate(nickname="Nonexistent")
        result = update_club(db=db, club_id=999, club=update_data)
        assert result is None

    def test_deactivate_club(self, db):
        """Test deactivating a club"""
        club_data = ClubCreate(nickname="To Deactivate", creator="deactivate_user")
        created_club = create_club(db=db, club=club_data)

        result = deactivate_club(db=db, club_id=created_club.id)

        assert result is not None
        assert result.active is False

        # Verify it's no longer returned by get_club
        retrieved_club = get_club(db=db, club_id=created_club.id)
        assert retrieved_club is None

    def test_deactivate_club_nonexistent(self, db):
        """Test deactivating a club that doesn't exist"""
        result = deactivate_club(db=db, club_id=999)
        assert result is None
