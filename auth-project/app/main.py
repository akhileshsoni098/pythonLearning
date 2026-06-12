# ============================================================
# main.py
# Kaam: FastAPI app, Routes (Endpoints), Server start
# ============================================================
# Yeh entry point hai. Yahan se:
# - FastAPI app create hota hai
# - Saare API endpoints (routes) define hote hain
# - Server start hota hai

# ------------------------------------------------------------------
# from fastapi import FastAPI, Depends, HTTPException, status
#
# FastAPI -> Main application class
#   🔧 app = FastAPI() -> app instance banao
#      @app.get("/") -> route register karo
#      uvicorn.run(app) -> server start karo
#
# Depends -> Dependency injection (auth.py se same)
# HTTPException -> Error response
# status -> HTTP status codes
# ------------------------------------------------------------------
from fastapi import FastAPI, Depends, HTTPException, status

# ------------------------------------------------------------------
# from fastapi.middleware.cors import CORSMiddleware
# 📌 CORS = Cross-Origin Resource Sharing
# 🔧 Frontend (React, Angular, etc.) alag port/domain pe chalega
#    Browser security policy frontend ko backend se connect nahi
#    hone deti. CORS middleware is problem ko solve karta hai.
# ------------------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

# ------------------------------------------------------------------
# from sqlalchemy.orm import Session
# 📌 Type hint ke liye
# 🔧 'db: Session' batata hai ki db ek SQLAlchemy Session object hai
# ------------------------------------------------------------------
from sqlalchemy.orm import Session

# ------------------------------------------------------------------
# from datetime import datetime
# 📌 datetime.utcnow() -> register time set karne ke liye
# ------------------------------------------------------------------
from datetime import datetime

# ------------------------------------------------------------------
# from app.database import ensure_database_exists, engine, Base, get_db
#
# ensure_database_exists -> database create kare (agar nahi hai to)
# engine -> SQLAlchemy engine (Base.metadata.create_all ke liye)
# Base -> declarative_base (create_all ke liye)
# get_db -> DB session provider (Depends(get_db) ke liye)
# ------------------------------------------------------------------
from app.database import ensure_database_exists, engine, Base, get_db

# ------------------------------------------------------------------
# from app.models import User
# 📌 SQLAlchemy User model
# 🔧 db.query(User) -> users table mein query karne ke liye
# ------------------------------------------------------------------
from app.models import User

# ------------------------------------------------------------------
# from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
# UserRegister  -> POST /register ka request body validate karega
# UserLogin     -> POST /login ka request body
# UserResponse  -> Response format (bina password ke)
# TokenResponse -> Login success pe token + user bhejega
# ------------------------------------------------------------------
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse

# ------------------------------------------------------------------
# from app.auth import hash_password, verify_password, create_access_token, get_current_user
# hash_password      -> password ko hash karega (register)
# verify_password    -> password match karega (login)
# create_access_token -> JWT token banayega (login)
# get_current_user   -> AUTH MIDDLEWARE (protected routes)
# ------------------------------------------------------------------
from app.auth import hash_password, verify_password, create_access_token, get_current_user

# ------------------------------------------------------------------
# import uvicorn
# 📌 ASGI server (jo actually HTTP requests sunta hai)
# 🔧 uvicorn.run("app.main:app", port=3001) -> server start
#    "app.main:app" ka matlab:
#       app package -> main module -> app variable (FastAPI instance)
# ------------------------------------------------------------------
import uvicorn


# ===================== DATABASE SETUP =========================

# Step 1: Ensure database exists
# ensure_database_exists() psycopg2 se check karta hai
# Agar python_auth_db nahi hai to CREATE DATABASE chalayega
ensure_database_exists()

# Step 2: Create all tables
# Base.metadata.create_all() check karta hai:
# - users table exist karta hai? -> nahi to CREATE TABLE chalayega
# - columns match karte hain? -> nahi to alter (with limitations)
create_all_result = Base.metadata.create_all(bind=engine)
print("[OK] Tables create/verify ho gayi!")


# ===================== FASTAPI APP ============================
app = FastAPI(
    title="Python Auth API",
    description="Register, Login, Profile - Complete Authentication System",
    version="1.0.0",
)

# CORS middleware - frontend ko allow karo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Sab domains allow (production mein specific do)
    allow_credentials=True,  # Cookies/auth headers allow
    allow_methods=["*"],     # Sab HTTP methods (GET, POST, etc.)
    allow_headers=["*"],     # Sab headers allow
)


# ===================== API ENDPOINTS ==========================

# ---------- 1. HOME (Health Check) ----------
@app.get("/")
def home():
    """Server chal raha hai ya nahi? Check karne ke liye."""
    return {
        "message": "Python Auth API chal raha hai!",
        "endpoints": {
            "POST /register": "Naya user register karein",
            "POST /login": "Login karein aur JWT token lein",
            "GET /profile": "Apna profile dekhein (token required)",
        },
        "docs": "/docs (Swagger UI)",
    }


# ---------- 2. REGISTER ----------
@app.post(
    "/register",
    response_model=UserResponse,       # Response format (bina password)
    status_code=status.HTTP_201_CREATED  # Success = 201 Created
)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    🔐 USER REGISTRATION

    ⚡ Pura flow (step by step):

    [REQUEST] POST /register
    Body: { "username": "akhilesh", "email": "...", "password": "...", ... }

    [1] FastAPI -> user_data: UserRegister
        -> Pydantic automatically validate karega:
           - Username format (3-30 chars, letters/digits/_)
           - Email format (basic pattern check)
           - Password strength (8+ chars, upper, lower, digit, special)
        -> Agar kuch galat hai -> 422 Validation Error auto

    [2] password == confirm_password check
        -> Agar match nahi karte -> 400 Bad Request

    [3] Username unique check
        -> SELECT * FROM users WHERE username = 'akhilesh'
        -> Agar already hai -> 400 Bad Request

    [4] Email unique check
        -> SELECT * FROM users WHERE email = 'akhilesh@example.com'
        -> Agar already hai -> 400 Bad Request

    [5] Password hash karo
        -> hash_password("Test@1234") -> "$2b$12$LJ3m..."

    [6] Naya User object banao
        User(username="akhilesh", email="...", hashed_password="$2b$12$...", ...)

    [7] Database mein save karo
        db.add(new_user)     -> INSERT query prepare
        db.commit()          -> Actually database mein save
        db.refresh(new_user) -> Naya data (jaise ID) refresh

    [8] Response bhejo (UserResponse format mein, PASSWORD NAHI BHEJNA!)
    """
    # Password match check
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password aur confirm password match nahi kar rahe",
        )

    # Username unique check
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already exists - koi aur chunein",
        )

    # Email unique check
    existing_email = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_data.email}' already registered hai - login karein",
        )

    # User create karo
    new_user = User(
        username=user_data.username,
        email=user_data.email.lower(),
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(new_user)      # Session mein add karo
    db.commit()            # Database mein save karo
    db.refresh(new_user)   # DB se naya data (ID, etc.) lo

    print(f"[OK] Naya user register hua: {new_user.username} ({new_user.email})")
    return new_user


# ---------- 3. LOGIN ----------
@app.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    🔑 USER LOGIN

    ⚡ Pura flow:

    [REQUEST] POST /login
    Body: { "username": "akhilesh", "password": "Test@1234" }

    [1] Database mein user dhundo
        -> SELECT * FROM users WHERE username = 'akhilesh'

    [2] Password verify karo
        -> verify_password("Test@1234", "$2b$12$LJ3m...")
        -> bcrypt internally compare karega
        -> Agar match nahi kiya -> 401 Unauthorized

    [3] Account active hai?
        -> user.is_active == True?
        -> Agar False -> 403 Forbidden

    [4] JWT access token banao
        -> create_access_token({"sub": "akhilesh"})
        -> Token mein encode hota hai:
           { "sub": "akhilesh", "exp": 1680000000 }
        -> SECRET_KEY se sign hota hai

    [5] Response bhejo
        {
          "access_token": "eyJhbGciOiJIUzI1NiJ9...",
          "token_type": "bearer",
          "user": { "id": 1, "username": "akhilesh", ... }
        }

    📌 Client is token ko save karega (localStorage, cookie, etc.)
        Aur har request mein bhejega:
        Header: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
    """
    # User dhundo
    user = db.query(User).filter(User.username == login_data.username).first()

    # Verify password (agar user exist karta hai to)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ya password galat hai",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Account active check
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled hai - admin se contact karein",
        )

    # JWT token banao
    access_token = create_access_token(data={"sub": user.username})

    print(f"[OK] User login successful: {user.username}")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


# ---------- 4. PROFILE (PROTECTED ROUTE) ----------
@app.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    👤 USER PROFILE - PROTECTED ROUTE

    Sirf valid JWT token wala user hi access kar sakta hai.

    ⚡ Pura flow:

    [REQUEST] GET /profile
    Header: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...

    [1] FastAPI dekhta hai: Depends(get_current_user)

    [2] get_current_user() call hota hai (auth.py se):
        a) HTTPBearer() -> header se token nikaalta hai
        b) verify_token() -> token decode/verify karta hai
        c) Username nikaalta hai "sub" field se
        d) Database se user dhunda hai
        e) User object return karta hai

    [3] Agar token valid hai:
        -> current_user mein User object milta hai
        -> Route function chalega
        -> UserResponse mein convert hoke JSON return hoga

    [4] Agar token invalid/missing/expired:
        -> verify_token() 401 error throw karega
        -> Route function chalega hi nahi
        -> Client ko error milega

    Test command:
    curl -X GET http://localhost:3001/profile \
      -H "Authorization: Bearer <TOKEN>"
    """
    return current_user


# ===================== START SERVER ===========================
if __name__ == "__main__":
    """
    Jab yeh file direct run karein to server start ho jayega.

    Commands:
      python -m app.main
      ya cd app && python main.py

    Server start hone ke baad:
    - http://localhost:3001/     -> Home page
    - http://localhost:3001/docs -> Swagger UI (API docs + test)
    - http://localhost:3001/redoc -> ReDoc (alt docs)

    SWAGGER UI BEST HAI!
    Wahan "Authorize" button hai -> waha "Bearer <token>" daalo
    Phir /profile direct test kar sakte ho!
    """
    print()
    print("=" * 60)
    print("  Python Auth API Server Start ho raha hai...")
    print(f"  Port: 3001")
    print(f"  Swagger Docs: http://localhost:3001/docs")
    print(f"  ReDoc: http://localhost:3001/redoc")
    print("=" * 60)
    print()

    uvicorn.run(
        "app.main:app",  # app package -> main module -> app variable
        host="0.0.0.0",  # Sab IP se access (0.0.0.0 = localhost)
        port=3001,
        reload=True,     # Code change -> auto restart (dev mode)
    )
