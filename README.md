# YoApunto API

A modern FastAPI-based REST API for managing clubs and games with comprehensive CRUD operations, many-to-many associations, validation, and soft delete functionality.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🗄️ **SQLAlchemy** - Powerful SQL toolkit and ORM with many-to-many relationships
- ✅ **Pydantic** - Data validation using Python type hints
- 🧪 **Comprehensive Testing** - Unit and integration tests with pytest organized by entity
- 🔄 **Soft Delete** - Clubs and games are deactivated, not permanently deleted
- 📝 **Input Validation** - Field length limits and required field validation
- 🏗️ **Clean Architecture** - Organized code structure with separation of concerns
- 📚 **Auto-generated Documentation** - Interactive API docs with Swagger UI
- 🔗 **Entity Associations** - Many-to-many relationships between clubs and games
- 🎮 **Game Management** - Complete game system with player/team composition rules

## Project Structure

```
api.yoapunto/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── clubs.py          # Club API endpoints
│   │       │   ├── games.py          # Game API endpoints
│   │       │   └── club_games.py     # Club-Game association endpoints
│   │       └── api.py                # API router configuration
│   ├── crud/
│   │   ├── club.py                   # Club database operations
│   │   └── game.py                   # Game database operations
│   ├── models/
│   │   ├── club.py                   # Club SQLAlchemy model
│   │   ├── game.py                   # Game SQLAlchemy model
│   │   └── club_games.py             # Many-to-many association table
│   └── schemas/
│       ├── club.py                   # Club Pydantic schemas
│       └── game.py                   # Game Pydantic schemas
├── tests/
│   ├── clubs/                        # Club-specific tests
│   │   ├── test_clubs_api.py         # Club API endpoint tests
│   │   ├── test_clubs_crud.py        # Club CRUD operation tests
│   │   ├── test_clubs_models.py      # Club model tests
│   │   └── test_clubs_games.py       # Club-Games association tests
│   ├── games/                        # Game-specific tests
│   │   ├── test_games_api.py         # Game API endpoint tests
│   │   ├── test_games_crud.py        # Game CRUD operation tests
│   │   ├── test_games_models.py      # Game model tests
│   │   └── test_games_clubs.py       # Game-Clubs relationship tests
│   └── conftest.py                   # Shared test configuration
├── conftest.py                       # Test configuration
├── database.py                       # Database setup
├── main.py                           # FastAPI application
├── requirements.txt                  # Python dependencies
└── pyproject.toml                    # Test configuration
```

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/api.yoapunto.git
   cd api.yoapunto
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

5. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation (Swagger UI):** `http://localhost:8000/docs`
- **Alternative API Documentation (ReDoc):** `http://localhost:8000/redoc`

## API Endpoints

### Clubs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/clubs/` | List all active clubs |
| `POST` | `/api/v1/clubs/` | Create a new club |
| `GET` | `/api/v1/clubs/{id}` | Get a specific club |
| `PUT` | `/api/v1/clubs/{id}` | Update a club |
| `DELETE` | `/api/v1/clubs/{id}` | Deactivate a club (soft delete) |

### Games

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/games/` | List all active games |
| `POST` | `/api/v1/games/` | Create a new game |
| `GET` | `/api/v1/games/{id}` | Get a specific game |
| `PUT` | `/api/v1/games/{id}` | Update a game |
| `DELETE` | `/api/v1/games/{id}` | Deactivate a game (soft delete) |

### Club-Games Associations (Nested Resources)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/clubs/{club_id}/games/` | Get all games that a club plays |
| `POST` | `/api/v1/clubs/{club_id}/games/{game_id}` | Add a game to a club |
| `GET` | `/api/v1/clubs/{club_id}/games/{game_id}` | Check if a club plays a specific game |
| `DELETE` | `/api/v1/clubs/{club_id}/games/{game_id}` | Remove a game from a club |

### Club Model

```json
{
  "id": 1,
  "nickname": "My Awesome Club",
  "creator": "john_doe",
  "thumbnail_url": "https://example.com/image.jpg",
  "active": true,
  "created_at": "2025-08-11T10:30:00Z",
  "updated_at": "2025-08-11T10:30:00Z"
}
```

### Game Model

```json
{
  "id": 1,
  "name": "Basketball",
  "description": "Team sport with two teams of five players",
  "game_composition": "team",
  "min_number_of_teams": 2,
  "max_number_of_teams": 2,
  "min_number_of_players": 10,
  "max_number_of_players": 10,
  "min_number_of_players_per_teams": 5,
  "max_number_of_players_per_teams": 5,
  "thumbnail": "https://example.com/basketball.jpg",
  "active": true,
  "created_at": "2025-08-13T10:30:00Z",
  "updated_at": "2025-08-13T10:30:00Z"
}
```

#### Field Validation

**Club Fields:**
- **nickname**: Required, 1-50 characters
- **creator**: Required, 1-50 characters
- **thumbnail_url**: Optional, URL to club image
- **active**: Boolean, defaults to `true`

**Game Fields:**
- **name**: Required, 1-100 characters
- **description**: Optional, up to 500 characters
- **game_composition**: Required, 1-50 characters (e.g., "player", "team", "player_or_team")
- **min_number_of_players**: Required, must be >= 1
- **max_number_of_players**: Optional, must be >= 1 if specified
- **min_number_of_teams**: Optional, must be >= 1 if specified
- **max_number_of_teams**: Optional, must be >= 1 if specified
- **min_number_of_players_per_teams**: Optional, must be >= 1 if specified
- **max_number_of_players_per_teams**: Optional, must be >= 1 if specified
- **thumbnail**: Optional, URL or path to game thumbnail image

### Example Requests

**Create a club:**
```bash
curl -X POST "http://localhost:8000/api/v1/clubs/" \
     -H "Content-Type: application/json" \
     -d '{
       "nickname": "Tech Enthusiasts",
       "creator": "alice_smith",
       "thumbnail_url": "https://example.com/tech-club.jpg"
     }'
```

**Create a game:**
```bash
curl -X POST "http://localhost:8000/api/v1/games/" \
     -H "Content-Type: application/json" \
     -d '{
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
     }'
```

**Add a game to a club:**
```bash
curl -X POST "http://localhost:8000/api/v1/clubs/1/games/1"
```

**Get all games for a club:**
```bash
curl "http://localhost:8000/api/v1/clubs/1/games/"
```

**Remove a game from a club:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/clubs/1/games/1"
```

## Database Configuration

The application supports both SQLite (for development) and PostgreSQL (for production).

### SQLite (Default)
```env
DATABASE_URL=sqlite:///./yoapunto.db
```

### PostgreSQL
```env
DATABASE_URL=postgresql://username:password@localhost/database_name
```

## Testing

The project includes comprehensive tests at multiple levels, organized by entity:

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Club tests
pytest tests/clubs -v

# Game tests
pytest tests/games -v

# API tests
pytest tests/test_accounts_api.py -v
```

### Run Tests with Coverage
```bash
pytest --cov=app
```

### Test Categories

- **Model Tests**: Test SQLAlchemy model validation and behavior
- **CRUD Tests**: Test database operations and business logic
- **API Tests**: Test HTTP endpoints, status codes, and response formats

## Development

### Code Organization

The project follows a clean architecture pattern:

- **`app/models/`**: SQLAlchemy models (database schema)
- **`app/schemas/`**: Pydantic models (API validation)
- **`app/crud/`**: Database operations (business logic)
- **`app/api/`**: FastAPI endpoints (HTTP layer)

### Adding New Features

1. **Add model** in `app/models/`
2. **Add schemas** in `app/schemas/`
3. **Add CRUD operations** in `app/crud/`
4. **Add API endpoints** in `app/api/v1/endpoints/`
5. **Add tests** in `tests/`

### Code Quality

The project includes:

- **Type hints** throughout the codebase
- **Pydantic validation** for all API inputs
- **Comprehensive testing** with high coverage
- **Clean architecture** with separation of concerns

## Deployment

### Environment Variables

Set these environment variables in production:

```env
DATABASE_URL=your_production_database_url
```

### Docker (Optional)

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Dependencies

### Core Dependencies
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **psycopg** - PostgreSQL adapter
- **python-dotenv** - Environment variable management

### Development Dependencies
- **pytest** - Testing framework
- **httpx** - HTTP client for testing
- **pytest-asyncio** - Async testing support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [API documentation](http://localhost:8000/docs) when running locally
2. Review the test files for usage examples
3. Open an issue on GitHub

## Roadmap

- [ ] Club membership management
- [ ] Enter Game integration
- [ ] Associate clubs with games where the relationship with clubs and games is many-to-many
- [ ] API rate limiting
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
