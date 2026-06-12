# Python Auth API - Complete Authentication System

Ek simple authentication API jo Register, Login aur Profile features provide karta hai JWT token ke saath.

---

## Project Structure

```
auth-project/
│
├── app/                          # Main application package
│   ├── __init__.py               # Package init (empty, tells Python it's a package)
│   ├── database.py               # Database connection, session, auto-create DB
│   ├── models.py                 # SQLAlchemy table models (User)
│   ├── schemas.py                # Pydantic models (request/response validation)
│   ├── auth.py                   # Password hashing, JWT token, Auth middleware
│   └── main.py                   # FastAPI app, routes (endpoints), server start
│
├── requirements.txt              # Python dependencies
├── README.md                     # Yeh file
└── venv/                         # Virtual environment (Python packages yahan install hote hain)
```

---

## File-by-File Explanation

### 1. `database.py` - Database Connection

**Kaam:** PostgreSQL se connect karna, database auto-create karna, aur har request ke liye session provide karna.

```
database.py
│
├── psycopg2 ───────────────────── Direct PostgreSQL connection (DB create karne ke liye)
│   └── ISOLATION_LEVEL_AUTOCOMMIT ─── CREATE DATABASE command ke liye zaroori
│
├── sqlalchemy ─────────────────── ORM framework
│   ├── create_engine() ─────────── Connection pool banata hai
│   ├── sessionmaker() ──────────── Har request ke liye session factory
│   └── declarative_base() ──────── Table models ke liye parent class
│
└── Functions:
    ├── ensure_database_exists() ── DB create kare (agar nahi hai)
    └── get_db() ────────────────── FastAPI dependency - har request mein naya session
```

### 2. `models.py` - Database Table Model

**Kaam:** `users` table ka structure define karta hai.

```
models.py
│
├── from sqlalchemy import Column, Integer, String, Boolean, DateTime
│   └── Column types jo database table mein columns banayenge
│
├── from datetime import datetime
│   └── datetime.utcnow() - created_at field ka default value
│
├── from app.database import Base
│   └── Parent class - isko extend karo to table banta hai
│
└── class User(Base):
    ├── __tablename__ = "users" ─── Table ka naam
    ├── id = Column(Integer, ...) ─── Primary key, auto-increment
    ├── username = Column(String(50), ...) ─── Unique username
    ├── email = Column(String(100), ...) ─── Unique email
    ├── hashed_password = Column(String(255), ...) ─── bcrypt hash
    ├── full_name = Column(String(100), ...) ─── Optional
    ├── is_active = Column(Boolean, ...) ─── Default True
    └── created_at = Column(DateTime, ...) ─── Auto set
```

### 3. `schemas.py` - Request/Response Validation

**Kaam:** Client se data lene aur bhejne ke format define karna. Pydantic auto-validate karta hai.

```
schemas.py
│
├── from pydantic import BaseModel, field_validator
│   ├── BaseModel ───── Parent class for all schemas
│   └── field_validator ── Field-level validation decorator
│
├── from datetime import datetime ── Type hint ke liye
│
├── import re ── Regular expressions (pattern matching)
│
├── Validation Helpers:
│   ├── validate_username() ──── 3-30 chars, letters/digits/_
│   ├── validate_email() ─────── Format check + lowercase
│   └── validate_password_strength() ── 8+ chars, upper, lower, digit, special
│
├── Request Schemas (input):
│   ├── class UserRegister ──── POST /register body
│   │   ├── username, email, password, confirm_password, full_name
│   │   └── field_validators for username, email, password
│   │
│   └── class UserLogin ─────── POST /login body
│       └── username, password
│
└── Response Schemas (output):
    ├── class UserResponse ──── User data (bina password!)
    │   └── model_config = {"from_attributes": True}
    │
    └── class TokenResponse ─── Token + User data
        └── access_token, token_type, user
```

### 4. `auth.py` - Authentication Logic

**Kaam:** Password hashing, JWT token creation/verification, aur auth middleware.

```
auth.py
│
├── from fastapi import Depends, HTTPException, status
│   ├── Depends ──────── Dependency injection
│   ├── HTTPException ── Error responses
│   └── status ───────── HTTP status codes
│
├── from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
│   ├── HTTPBearer ─────────── Auto-extract Authorization header
│   └── HTTPAuthorizationCredentials ── Type hint
│
├── from jose import JWTError, jwt
│   ├── jwt.encode() ──── Token banaye
│   ├── jwt.decode() ──── Token verify kare
│   └── JWTError ──────── Invalid token exception
│
├── from passlib.context import CryptContext
│   ├── .hash(password) ──── Hash generate
│   └── .verify(plain, hash) ── Compare
│
├── from datetime import datetime, timedelta
│   └── Token expiry calculate karne ke liye
│
├── from sqlalchemy.orm import Session ── Type hint
├── from app.database import get_db ──── DB session
├── from app.models import User ──────── User table model
│
├── Password Functions:
│   ├── hash_password(password) ── bcrypt hash banaye
│   └── verify_password(plain, hash) ── Match check kare
│
├── JWT Functions:
│   ├── create_access_token(data) ── JWT token generate kare
│   │   └── data = {"sub": username} + expiry time
│   │
│   └── verify_token(token) ── Decode + verify kare
│       └── Return {"username": "..."} ya 401 error
│
└── Auth Middleware:
    └── get_current_user() ── Protected routes ka guard
        ├── Takes: token (from HTTPBearer), db (from get_db)
        ├── Steps: verify_token -> get username -> query DB -> return user
        └── Error: 401 agar token invalid, 404 agar user nahi mila
```

### 5. `main.py` - FastAPI App & Routes

**Kaam:** Server start karna, saare API endpoints define karna.

```
main.py
│
├── Imports:
│   ├── FastAPI, Depends, HTTPException, status ─── FastAPI core
│   ├── CORSMiddleware ──────────────────────── CORS fix
│   ├── Session ─────────────────────────────── Type hint
│   ├── datetime ────────────────────────────── Timestamp
│   ├── From app.database ───────────────────── DB functions
│   ├── From app.models ─────────────────────── User model
│   ├── From app.schemas ────────────────────── Request/Response schemas
│   ├── From app.auth ───────────────────────── Auth functions
│   └── uvicorn ─────────────────────────────── ASGI server
│
├── Setup:
│   ├── ensure_database_exists() ── DB create (agar nahi)
│   └── Base.metadata.create_all() ── Tables create
│
├── CORS Middleware ── Frontend ko allow kare
│
├── Routes (Endpoints):
│   │
│   ├── GET  / ──────── Home / Health Check
│   │   └── Return: endpoints list
│   │
│   ├── POST /register ─── Register naya user
│   │   ├── Request: {username, email, password, confirm_password, full_name?}
│   │   ├── Validation: Pydantic (schema) + manual (uniqueness, password match)
│   │   ├── Process: hash password -> create User -> db.save -> return UserResponse
│   │   └── Response: {id, username, email, full_name, is_active, created_at}
│   │
│   ├── POST /login ─── Login, get JWT token
│   │   ├── Request: {username, password}
│   │   ├── Process: find user -> verify password -> create JWT -> return TokenResponse
│   │   └── Response: {access_token, token_type, user}
│   │
│   └── GET  /profile ─── Protected - get current user's profile
│       ├── Header: Authorization: Bearer <token>
│       ├── Middleware: get_current_user() verify karega
│       └── Response: {id, username, email, full_name, is_active, created_at}
│
└── Server Start:
    └── uvicorn.run("app.main:app", port=3001, reload=True)
```

---

## Complete Request Flow

Jab koi request aati hai, to pura flow kuch aisa hota hai:

### Register Flow (POST /register)

```
Client                          Server (FastAPI)
  │                                  │
  │  POST /register                  │
  │  { "username": "akhilesh",       │
  │    "email": "a@b.com",           │
  │    "password": "Test@1234",      │
  │    "confirm_password": "Test@1234" }
  │                                  │
  │ ──────────────────────────────>  │
  │                                  │
  │                           [1] FastAPI receives request
  │                                  │
  │                           [2] main.py ka register_user()
  │                               route match hota hai
  │                                  │
  │                           [3] user_data: UserRegister
  │                               Pydantic validate karta hai:
  │                               - username: 3-30 chars ✓
  │                               - email: valid format ✓
  │                               - password: strong ✓
  │                                  │
  │                           [4] db: Session = Depends(get_db)
  │                               database.py -> naya session
  │                                  │
  │                           [5] Password match check (main.py)
  │                                  │
  │                           [6] Username unique check
  │                               db.query(User).filter(...)
  │                               (models.py ka User use hua)
  │                                  │
  │                           [7] Email unique check
  │                                  │
  │                           [8] hash_password("Test@1234")
  │                               auth.py -> bcrypt hash
  │                                  │
  │                           [9] User object create
  │                               models.py ka User class
  │                                  │
  │                          [10] db.add(), db.commit()
  │                               database mein save
  │                                  │
  │                          [11] Return UserResponse
  │                               schemas.py (bina password)
  │                                  │
  │  Response 201                    │
  │  { "id": 1, "username": "akhilesh", ... }
  │ <──────────────────────────────  │
```

### Login Flow (POST /login)

```
Client                          Server
  │                                  │
  │  POST /login                     │
  │  { "username": "akhilesh",       │
  │    "password": "Test@1234" }     │
  │                                  │
  │ ──────────────────────────────>  │
  │                                  │
  │                           [1] main.py -> login_user()
  │                                  │
  │                           [2] UserLogin validate (schemas.py)
  │                                  │
  │                           [3] db.query(User).filter(...)
  │                               User dhunda (models.py)
  │                                  │
  │                           [4] verify_password() (auth.py)
  │                               bcrypt compare
  │                                  │
  │                           [5] Check user.is_active
  │                                  │
  │                           [6] create_access_token() (auth.py)
  │                               JWT token bana:
  │                               encode({"sub":"akhilesh","exp":...})
  │                                  │
  │                           [7] Return TokenResponse (schemas.py)
  │                               { access_token, token_type, user }
  │                                  │
  │  Response 200                    │
  │  { "access_token": "eyJ...",     │
  │    "token_type": "bearer",       │
  │    "user": { "id": 1, ... } }    │
  │ <──────────────────────────────  │
  │                                  │
  │ [Client token save karta hai]    │
```

### Profile Flow (GET /profile) - Protected Route

```
Client                          Server
  │                                  │
  │  GET /profile                    │
  │  Authorization: Bearer eyJ...    │
  │                                  │
  │ ──────────────────────────────>  │
  │                                  │
  │                           [1] main.py -> get_profile()
  │                               Dekhta hai: Depends(get_current_user)
  │                                  │
  │                           [2] get_current_user() (auth.py)
  │                               ─── AUTH MIDDLEWARE ───
  │                                  │
  │                           [3] HTTPBearer() (fastapi.security)
  │                               Header se token nikaala:
  │                               "eyJhbGciOiJIUzI1NiJ9..."
  │                                  │
  │                           [4] verify_token(token) (auth.py)
  │                               jwt.decode() kiya:
  │                               - Signature verify ✓
  │                               - Expiry check ✓
  │                               - Username: "akhilesh"
  │                                  │
  │                           [5] db.query(User).filter(...)
  │                               Database se user dhunda
  │                                  │
  │                           [6] User mil gaya -> return
  │                                  │
  │                           ─── END AUTH MIDDLEWARE ───
  │                                  │
  │                           [7] Ab route function chalega
  │                               current_user = User object
  │                               return current_user
  │                                  │
  │                           [8] UserResponse mein convert (schemas.py)
  │                                  │
  │  Response 200                    │
  │  { "id": 1, "username": "akhilesh", ... }
  │ <──────────────────────────────  │
```

---

## How Files Connect With Each Other

```
┌─────────────────────────────────────────────────────────────────────┐
│                        main.py (Entry Point)                        │
│                                                                     │
│  from app.database import ensure_database_exists, engine, Base,     │
│                               get_db                                │
│  from app.models import User                                        │
│  from app.schemas import UserRegister, UserLogin, UserResponse,     │
│                           TokenResponse                            │
│  from app.auth import hash_password, verify_password,               │
│                         create_access_token, get_current_user       │
│                                                                     │
│  Saare modules ko import karta hai                                  │
│  Routes define karta hai                                            │
└──────────┬──────────────┬─────────────────┬────────────────┬────────┘
           │              │                 │                │
           ▼              ▼                 ▼                ▼
┌──────────────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐
│   database.py    │ │models.py │ │ schemas.py   │ │   auth.py    │
│                  │ │          │ │              │ │              │
│ Engine/Session   │ │ User     │ │ Request/     │ │ Password     │
│ Base (parent)    │ │ class    │ │ Response     │ │ Hash/JWT     │
│ get_db()         │ │ (table)  │ │ Validation   │ │ Middleware   │
│                  │ │          │ │              │ │              │
│ ◄────engine────► │ │ ◄─Base──► │ │              │ │ ◄──get_db──► │
│ ◄───get_db()───► │ │          │ │              │ │ ◄──User────► │
└──────────────────┘ └──────────┘ └──────────────┘ └──────────────┘
        │                                                    │
        ▼                                                    ▼
┌──────────────────┐                                ┌──────────────┐
│   PostgreSQL     │                                │   JWT Token  │
│   Database       │                                │   "eyJhb..." │
│                  │                                │              │
│ python_auth_db   │                                │ SECRET_KEY   │
│   └─ users table │                                │ se signed    │
└──────────────────┘                                └──────────────┘
```

### Dependency Chain

```
database.py     ← SQLAlchemy, psycopg2 (external packages)
     │
     ▼
models.py       ← database.py (imports Base)
     │
     ▼
schemas.py      ← pydantic, re, datetime (external + built-in)
     │
     ▼
auth.py         ← database.py (get_db), models.py (User)
                   fastapi, jose, passlib (external)
     │
     ▼
main.py         ← database.py, models.py, schemas.py, auth.py
                   fastapi, uvicorn (external)
```

---

## How to Run

### 1. Virtual Environment (First time only)

```bash
cd auth-project
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Server

```bash
python -m app.main
```

Server start hote hi:
- **API:** http://localhost:3001/
- **Swagger UI:** http://localhost:3001/docs (Yahan se direct test kar sakte ho!)
- **ReDoc:** http://localhost:3001/redoc

### 4. Test with curl

```bash
# Register
curl -X POST http://localhost:3001/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"akhilesh\",\"email\":\"akhilesh@example.com\",\"password\":\"Test@1234\",\"confirm_password\":\"Test@1234\",\"full_name\":\"Akhilesh Soni\"}"

# Login (response se token copy karo)
curl -X POST http://localhost:3001/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"akhilesh\",\"password\":\"Test@1234\"}"

# Profile (token laga ke)
curl -X GET http://localhost:3001/profile ^
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..."
```

---

## Key Concepts Summary

| Concept | File | Explanation |
|---------|------|-------------|
| **ORM** | `models.py` | Database table ko Python class ki tarah use karo |
| **Pydantic** | `schemas.py` | Data validation aur serialization |
| **Dependency Injection** | `auth.py`, `main.py` | FastAPI ka `Depends()` - functions ko pehle call karo |
| **JWT** | `auth.py` | JSON Web Token - user verify karne ka secure tarika |
| **Auth Middleware** | `auth.py` | `get_current_user()` - protected routes ka guard |
| **bcrypt** | `auth.py` | Password hashing algorithm (slow = secure) |
| **CORS** | `main.py` | Cross-Origin Resource Sharing - frontend ko allow karo |
