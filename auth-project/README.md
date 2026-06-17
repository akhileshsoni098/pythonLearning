# Auth API - Python FastAPI Authentication System

FastAPI-based authentication system with JWT tokens, user registration, login, and profile management using PostgreSQL.

---

## Project Structure

```
auth-project/
├── .env                          # Environment variables (DB creds, JWT secret)
├── requirements.txt              # Python dependencies
├── app/
│   ├── main.py                   # FastAPI entry point, middleware, router setup
│   ├── db/
│   │   ├── database.py           # PostgreSQL connection & table creation
│   │   ├── db_query.py           # Raw SQL query helper (supports dict cursor)
│   │   └── schemas/
│   │       ├── 01_users.sql      # users table DDL
│   │       └── 02_user_profiles.sql  # user_profiles table DDL
│   ├── middleware/
│   │   └── auth_deps.py          # Auth dependency (Bearer token → verify → payload)
│   ├── models/
│   │   ├── user_auth_model.py    # Pydantic models (RegisterModel, LoginModel)
│   │   └── user_profile_model.py # Pydantic model (profileModel)
│   ├── routes/
│   │   ├── auth_routes.py        # POST /auth/register, POST /auth/login
│   │   └── user_profile_routes.py # GET/POST /api/profile, /api/items, /api/user/{id}
│   └── utils/
│       ├── hash.py               # bcrypt password hashing
│       └── jwt.py                # JWT create & verify
└── README.md
```

---

## Environment Variables (.env)

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=python_db_connection
DB_USER=postgres
DB_PASSWORD=your_password

SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
```

---

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|:---:|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | Login, returns JWT token |
| GET | `/api/profile` | Yes | Get profile data |
| POST | `/api/profile` | Yes | Create/Update profile |
| GET | `/api/items` | Yes | Paginated items (demo) |
| POST | `/api/user/{id}` | No | Update user (demo) |

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "role": "user",
  "is_active": true
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Get Profile (Protected)

```http
GET /api/profile
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "data": {
    "id": 1,
    "user_id": 24,
    "name": "John Doe",
    "gender": "male",
    "phone": "1234567890",
    "created_at": "2026-06-16T...",
    "updated_at": "2026-06-16T..."
  }
}
```

### Create/Update Profile (Protected)

```http
POST /api/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 24,
  "name": "John Doe",
  "gender": "male",
  "phone": "1234567890"
}
```

---

## How Auth Works

```
Client                          Server
  │                                │
  │  POST /auth/login              │
  │  { email, password }           │
  │ ──────────────────────────>    │
  │                                │
  │                       [1] Verify email + password
  │                       [2] Create JWT token
  │                       [3] Return { access_token }
  │                                │
  │  <──────────────────────────   │
  │  { access_token: "eyJ..." }    │
  │                                │
  │  GET /api/profile              │
  │  Authorization: Bearer eyJ...  │
  │ ──────────────────────────>    │
  │                                │
  │                       [4] auth_deps.py → verify_token()
  │                       [5] JWT decode → {"user_id", "email"}
  │                       [6] Attach to req.state.user
  │                       [7] Return profile data
  │                                │
  │  <──────────────────────────   │
  │  { data: { id, name, ... } }   │
```

---

## Database Tables

### users

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | Primary Key |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | TEXT | bcrypt hash |
| role | VARCHAR(10) | 'user' or 'admin' |
| is_active | BOOLEAN | Default TRUE |
| created_at | TIMESTAMP | Auto |

### user_profiles

| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | Primary Key |
| user_id | INT | UNIQUE, FK → users(id) |
| name | VARCHAR(100) | NOT NULL |
| gender | VARCHAR(10) | 'male', 'female', 'other' |
| phone | VARCHAR(20) | NOT NULL |
| created_at | TIMESTAMP | Auto |
| updated_at | TIMESTAMP | Auto |

---

## How to Run

### 1. Setup

```bash
cd auth-project
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**Note:** Make sure PostgreSQL is running on port 5432.

### 2. Start Server

```bash
uvicorn app.main:app --reload
```

Server starts at: `http://localhost:8000`

### 3. Test with Swagger UI

Open `http://localhost:8000/docs` — interactive API documentation.

### 4. Test with curl

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"

# Login (copy token from response)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"

# Profile (with token)
curl -X GET http://localhost:8000/api/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..."
```

---

## Key Concepts

| Concept | Location | Description |
|---------|----------|-------------|
| **Pydantic** | `models/*.py` | Request/response data validation |
| **JWT** | `utils/jwt.py` | Token create & verify (HS256) |
| **bcrypt** | `utils/hash.py` | Password hashing |
| **Auth Middleware** | `middleware/auth_deps.py` | Bearer token → payload → `req.state.user` |
| **Raw SQL** | `db/db_query.py` | psycopg2 direct queries (supports dict cursor) |
| **Auto DB** | `db/database.py` | Auto-create database & tables on startup |
