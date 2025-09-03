# YoApunto API

A comprehensive FastAPI application for managing clubs, games, accounts, and authentication. This API provides secure user management, club administration, and game catalog functionality with JWT-based authentication.

## Features

- 🔐 **JWT Authentication & Authorization** (login, logout, token refresh)
- 👥 **User Account Management** (registration, profile updates, password changes)
- 🏟️ **Club Management** (create, update, soft delete clubs)
- 🎮 **Game Catalog** (manage available games and their configurations)
- 🔗 **Club-Game Relationships** (associate games with clubs)
- 🛡️ **Security Features** (password hashing with bcrypt, email validation)
- 📧 **Email Verification** (request and confirm email verification)
- 🔄 **Password Reset** (secure password reset functionality)
- 🔄 **Token Refresh** (secure token renewal system)
- 🗑️ **Soft Delete** (accounts, clubs, and games can be deactivated instead of deleted)
- ✅ **Comprehensive Testing** (127+ tests with excellent coverage)

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Primary database (SQLite for testing)
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type hints
- **JWT** - JSON Web Tokens for authentication
- **Bcrypt** - Secure password hashing
- **Pytest** - Testing framework

## Project Structure

```
api.yoapunto/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── accounts.py       # Account management endpoints
│   │   │   ├── clubs.py          # Club management endpoints
│   │   │   ├── games.py          # Game catalog endpoints
│   │   │   └── club_games.py     # Club-game relationship endpoints
│   │   └── api.py                # API router configuration
│   ├── crud/
│   │   ├── account.py            # Account database operations
│   │   ├── club.py               # Club database operations
│   │   ├── game.py               # Game database operations
│   │   └── club_game.py          # Club-game relationship operations
│   ├── models/
│   │   ├── account.py            # Account SQLAlchemy model
│   │   ├── club.py               # Club SQLAlchemy model
│   │   ├── game.py               # Game SQLAlchemy model
│   │   └── club_game.py          # Club-game relationship model
│   ├── schemas/
│   │   ├── account.py            # Account Pydantic schemas
│   │   ├── club.py               # Club Pydantic schemas
│   │   ├── game.py               # Game Pydantic schemas
│   │   └── club_game.py          # Club-game relationship schemas
│   └── auth_helper.py            # JWT and authentication utilities
├── tests/
│   ├── auth/                     # Authentication tests
│   ├── accounts/                 # Account tests
│   ├── clubs/                    # Club tests
│   ├── games/                    # Game tests
│   └── club_games/               # Club-game relationship tests
├── alembic/                      # Database migrations
├── database.py                   # Database configuration
├── main.py                       # FastAPI application entry point
└── requirements.txt              # Python dependencies
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd api.yoapunto
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and JWT configuration
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server:**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API docs (ReDoc):** http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Authenticate user and receive JWT token
- `POST /api/v1/auth/logout` - Logout (client-side token invalidation)
- `POST /api/v1/auth/refresh` - Refresh access token using refresh token
- `POST /api/v1/auth/password-reset/request` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset
- `POST /api/v1/auth/verify-email/request` - Request email verification
- `POST /api/v1/auth/verify-email/confirm` - Confirm email verification

### Accounts

- `GET /api/v1/accounts/` - List all active accounts
- `POST /api/v1/accounts/` - Create a new account (registration)
- `GET /api/v1/accounts/{id}` - Get account details
- `PUT /api/v1/accounts/{id}` - Update account information
- `DELETE /api/v1/accounts/{id}` - Deactivate account (soft delete)
- `GET /api/v1/accounts/club/{club_id}` - Get accounts for a specific club

### Clubs

- `GET /api/v1/clubs/` - List all active clubs
- `POST /api/v1/clubs/` - Create a new club
- `GET /api/v1/clubs/{id}` - Get club details
- `PUT /api/v1/clubs/{id}` - Update club information
- `DELETE /api/v1/clubs/{id}` - Deactivate club (soft delete)

### Games

- `GET /api/v1/games/` - List all active games
- `POST /api/v1/games/` - Create a new game
- `GET /api/v1/games/{id}` - Get game details
- `PUT /api/v1/games/{id}` - Update game information
- `DELETE /api/v1/games/{id}` - Deactivate game (soft delete)

### Club-Game Relationships

- `GET /api/v1/clubs/{club_id}/games` - Get games associated with a club
- `POST /api/v1/clubs/{club_id}/games` - Associate a game with a club
- `DELETE /api/v1/clubs/{club_id}/games/{game_id}` - Remove game from club

## Data Models

### Account Model
```json
{
  "id": 1,
  "email_address": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "club_id": 1,
  "active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null
}
```

### Club Model
```json
{
  "id": 1,
  "nickname": "Basketball Club",
  "creator": "John Doe",
  "thumbnail_url": "https://example.com/club-image.jpg",
  "active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null
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
  "thumbnail": "https://example.com/basketball.jpg",
  "active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": null
}
```

## Field Validation

### Account Fields
- **email_address**: Must be valid email format, unique across system
- **first_name**: 1-50 characters, required
- **last_name**: 1-50 characters, required
- **password**: 8-100 characters (stored as bcrypt hash), required for creation
- **club_id**: Optional foreign key to Club model

### Club Fields
- **nickname**: 1-100 characters, required
- **creator**: 1-100 characters, required
- **thumbnail_url**: Valid URL format, optional

### Game Fields
- **name**: 1-100 characters, required
- **description**: Optional text description
- **game_composition**: Required (individual, team, group)
- **min_number_of_teams**: Optional integer, minimum 1
- **max_number_of_teams**: Optional integer, must be >= min_number_of_teams
- **min_number_of_players**: Required integer, minimum 1
- **max_number_of_players**: Optional integer, must be >= min_number_of_players
- **thumbnail**: Optional URL for game image

## Example Requests

### Authentication

#### Register Account
```bash
curl -X POST http://localhost:8000/api/v1/accounts/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "newuser@example.com",
    "password": "securepassword123",
    "first_name": "Jane",
    "last_name": "Smith",
    "club_id": 1
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "user@example.com",
    "password": "securepassword123"
  }'
```

#### Use JWT Token
```bash
curl -X GET http://localhost:8000/api/v1/accounts/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Account Management

#### Update Account
```bash
curl -X PUT http://localhost:8000/api/v1/accounts/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "first_name": "UpdatedName",
    "email_address": "updated@example.com"
  }'
```

#### Change Password
```bash
curl -X PUT http://localhost:8000/api/v1/accounts/1/password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "current_password": "oldpassword123",
    "new_password": "newpassword123"
  }'
```

### Club Management

#### Create Club
```bash
curl -X POST http://localhost:8000/api/v1/clubs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "nickname": "Soccer Club",
    "creator": "Club Founder",
    "thumbnail_url": "https://example.com/soccer-club.jpg"
  }'
```

### Game Management

#### Create Game
```bash
curl -X POST http://localhost:8000/api/v1/games/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Soccer",
    "description": "The world's most popular sport",
    "game_composition": "team",
    "min_number_of_teams": 2,
    "max_number_of_teams": 2,
    "min_number_of_players": 22,
    "max_number_of_players": 22,
    "thumbnail": "https://example.com/soccer.jpg"
  }'
```

## Testing

Run the complete test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/auth/ -v           # Authentication tests
pytest tests/accounts/ -v       # Account tests
pytest tests/clubs/ -v          # Club tests
pytest tests/games/ -v          # Game tests

# Run tests with detailed output
pytest -v --tb=short
```

### Test Categories
- **Authentication Tests**: JWT token creation, validation, login/logout flows
- **Account Tests**: User registration, profile management, password changes
- **Club Tests**: Club CRUD operations and relationships
- **Game Tests**: Game catalog management and validation
- **Integration Tests**: End-to-end API workflow testing

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost/yoapunto
TEST_DATABASE_URL=sqlite:///./test.db

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (for verification and password reset)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Dependencies

```
fastapi==0.112.0
uvicorn==0.30.1
sqlalchemy==2.0.31
alembic==1.13.2
psycopg[binary]==3.2.9
python-dotenv==1.0.1
pydantic==2.8.2
email-validator==2.1.0

# Testing dependencies
pytest==8.3.2
pytest-asyncio==0.23.8
httpx==0.27.0
pytest-mock==3.14.0
pytest-cov==5.0.0

# Authentication dependencies
python-jose[cryptography]==3.3.0
python-multipart==0.0.9
bcrypt==4.3.0
passlib[bcrypt]==1.7.4
```

## Security Features

- 🔐 **JWT Authentication**: Secure token-based authentication
- 🛡️ **Password Hashing**: Bcrypt with salt for secure password storage
- 📧 **Email Validation**: Robust email format validation
- 🔄 **Token Refresh**: Secure token renewal without re-authentication
- 🚫 **Soft Delete**: Data preservation with deactivation instead of deletion
- ✅ **Input Validation**: Comprehensive Pydantic validation for all inputs
- 🔒 **CORS Protection**: Configurable cross-origin request handling

## API Versioning

The API is versioned using URL prefixes:
- Current version: `/api/v1/`
- Future versions can be added as `/api/v2/` etc.

## Error Handling

The API returns consistent error responses:

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation errors)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Submit a pull request

## Roadmap

- [x] JWT authentication system
- [x] Account management with secure password handling
- [x] Club and game management
- [x] Comprehensive test suite
- [x] Token refresh functionality
- [x] Email verification system
- [x] Password reset functionality
- [ ] Role-based access control (admin, member, etc.)
- [ ] Email notifications and templates
- [ ] API monitoring and logging
- [ ] File upload for club/game thumbnails

## License

This project is licensed under the MIT License - see the LICENSE file for details.
