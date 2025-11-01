# Email Classification API

A FastAPI project for email classification with modular architecture.

## Project Structure

```
Backend/
├── core/               # Core utilities and configurations
│   ├── config.py       # Application settings
│   ├── database.py     # Database configuration
│   ├── dependencies.py # Shared dependencies
│   └── security.py     # Security utilities
├── modules/             # Application modules
│   ├── auth/           # Authentication module
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── router.py
│   ├── users/          # Users module
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── router.py
│   └── parsing/        # Email parsing module
│       ├── models.py
│       ├── schemas.py
│       ├── service.py
│       └── router.py
└── main.py             # Main application file
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment file:
```bash
cp .env.example .env
```

5. Update `.env` with your configuration values.

## Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Register a new user
- `POST /login` - Login and get access token
- `GET /me` - Get current user (requires authentication)

### Users (`/api/v1/users`)
- `GET /` - Get all users
- `GET /{user_id}` - Get user by ID
- `PUT /{user_id}` - Update user
- `DELETE /{user_id}` - Delete user

### Parsing (`/api/v1/parsing`)
- `POST /` - Create email record
- `GET /` - Get all emails
- `GET /{email_id}` - Get email by ID
- `PUT /{email_id}/classify` - Classify email
- `PATCH /{email_id}` - Update email classification

## Development

The project uses:
- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **Pydantic** for data validation
- **JWT** for authentication
- **bcrypt** for password hashing

