# ============================================================
# auth.py
# Kaam: Password hashing, JWT token, Auth middleware
# ============================================================
# Is file mein saara authentication logic:
#   1. Password hash karna aur verify karna (bcrypt)
#   2. JWT token banana aur verify karna
#   3. get_current_user() -> yehi hai AUTH MIDDLEWARE

# ------------------------------------------------------------------
# from fastapi import Depends, HTTPException, status
#
# Depends -> FastAPI ka Dependency Injection system
#   🔧 Koi bhi function ko route se pehle call kara sakte ho
#      Jaise: get_current_user() har protected route se pehle chalega
#   ❓ Kyun? Code reuse, middleware, authentication sab isse easy ho jata hai
#
# HTTPException -> Error response bhejne ka FastAPI ka tarika
#   🔧 raise HTTPException(status_code=401, detail="msg")
#      -> Turant 401 response bhej dega, aage ka code nahi chalega
#
# status -> HTTP status codes ka collection
#   🔧 status.HTTP_401_UNAUTHORIZED = 401
#      status.HTTP_404_NOT_FOUND   = 404
#   👍 Fayda: Numbers yaad rakhne ki zaroorat nahi
# ------------------------------------------------------------------
from fastapi import Depends, HTTPException, status

# ------------------------------------------------------------------
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
#
# HTTPBearer -> FastAPI ka built-in security scheme
#   🔧 Automatically request ka 'Authorization' header check karta hai
#      Expected format: "Authorization: Bearer <token>"
#      Agar header nahi hai -> 403 error auto bhej dega
#   Detects: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
#
# HTTPAuthorizationCredentials -> type hint ke liye
#   🔧 Iske .credentials field mein actual token string milti hai
# ------------------------------------------------------------------
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ------------------------------------------------------------------
# from jose import JWTError, jwt
#
# jose = Javascript Object Signing and Encryption library
#   Yeh JWT token create/verify karta hai
#
# jwt -> main module
#   jwt.encode(payload, key, algorithm) -> token BANATA hai
#   jwt.decode(token, key, algorithms)  -> token VERIFY karta hai
#
# JWTError -> Exception class
#   🔧 Jab token invalid/expired ho to jwt.decode() yeh throw karta hai
#      Humein ise catch karna hai aur 401 error return karna hai
# ------------------------------------------------------------------
from jose import JWTError, jwt

# ------------------------------------------------------------------
# from passlib.context import CryptContext
#
# passlib = Python ka password hashing library
# CryptContext = hashing algorithms ka context/configuration
#
# 🔧 CryptContext(schemes=["bcrypt"], deprecated="auto")
#    Iska matlab: bcrypt algorithm use karo
#    deprecated="auto" -> automatically old algorithms handle karega
#
# 📌 bcrypt kyun?
#    - Slow hai (deliberately) -> hacker ke liye mushkil
#    - Auto-generates random salt (same password -> different hash)
#    - Industry standard for password hashing
#
# Methods:
#   .hash(password) -> hash string generate karta hai
#   .verify(password, hash) -> match karta hai ya nahi (True/False)
# ------------------------------------------------------------------
from passlib.context import CryptContext

# ------------------------------------------------------------------
# from datetime import datetime, timedelta
#
# datetime -> date/time operations
#   datetime.utcnow() -> current UTC time (GMT)
#
# timedelta -> time difference/interval
#   timedelta(minutes=60) -> 60 minute ka interval
#   🔧 Token expiry time calculate karne ke liye:
#      expire = datetime.utcnow() + timedelta(minutes=60)
#      -> Abhi se 60 minute baad ka time
# ------------------------------------------------------------------
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# from sqlalchemy.orm import Session
# 📌 Type hint ke liye
# 🔧 get_db() function Session type return karta hai
#    Isliye db parameter ko Session type dena best practice hai
# ------------------------------------------------------------------
from sqlalchemy.orm import Session

# ------------------------------------------------------------------
# from app.database import get_db
# 📌 database.py se get_db function import
# 🔧 get_db() ek generator hai jo DB session provide karta hai
#    'Depends(get_db)' lagao to automatically session mil jayega
# ------------------------------------------------------------------
from app.database import get_db

# ------------------------------------------------------------------
# from app.models import User
# 📌 models.py se User table model import
# 🔧 Database query ke liye chahiye:
#    db.query(User).filter(...).first()
# ------------------------------------------------------------------
from app.models import User


# ===================== CONFIGURATION ==========================
# SECRET_KEY: JWT sign karne ke liye (production mein .env mein daalo!)
SECRET_KEY = "aapkaSecretKeyYahaDaalein_1234567890"
ALGORITHM = "HS256"               # JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expiry: 1 ghanta


# ===================== PASSWORD HASHING =======================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Plain text password ko HASH karta hai (one-way encryption)

    Example:
      Input:  "Test@1234"
      Output: "$2b$12$LJ3m8x[...]5S6q" (60 chars ka random string)

    📌 One-way matlab?
      Isko reverse nahi kiya ja sakta (unhash nahi kar sakte)
      Sirf compare kar sakte ho: verify(plain, hash) -> True/False
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Login time pe check karta hai:
    User ne jo password dala -> kya woh database wale hash se match karta hai?

    compare(plain, hash) internally:
    1. Hash se salt nikaalta hai
    2. Plain password + salt ko hash karta hai
    3. Dono hash ko compare karta hai
    4. True/False return karta hai
    """
    return pwd_context.verify(plain_password, hashed_password)


# ===================== JWT TOKEN ==============================
# JWT = JSON Web Token
# Structure: base64(header).base64(payload).signature
# Example: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJha2hpbGVzaCJ9.xxxxx

def create_access_token(data: dict) -> str:
    """
    JWT access token GENERATE karta hai

    data = { "sub": "username" }
      'sub' (subject) = JWT Standard Claim
      Isme user ka unique identifier store karte hain (yahan username)

    Token mein expiry time bhi add hoti hai:
      'exp' (expiration) = bhi JWT Standard Claim
      jab tak ka token valid hai

    Output:
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha2hpbGVzaCIsImV4cCI6MTY4MDAwMDB9.xxxx"

    Client is token ko save karega aur har request mein bhejega.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """
    JWT token VERIFY karta hai

    Steps:
    1. Token decode karo SECRET_KEY se
    2. Check karo: signature valid hai?
    3. Check karo: token expire to nahi hua? ('exp' check hota hai)
    4. 'sub' field se username nikaalo
    5. Return karo {"username": "..."}

    Agar kuch bhi galat hai -> 401 Unauthorized error
    """
    try:
        # jwt.decode() automatically:
        # - Signature verify karega
        # - Expiry check karega (exp field)
        # - Agar invalid -> JWTError throw karega
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalid hai - username nahi mila",
            )
        return {"username": username}

    except JWTError:
        # Token expire ho gaya ya signature galat hai
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid hai ya expire ho gaya hai",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ===================== AUTH MIDDLEWARE ========================
# HTTPBearer() ek FastAPI dependency hai jo:
# 1. Request ka 'Authorization' header check karti hai
# 2. Expected: "Authorization: Bearer <token>"
# 3. Token nikaal kar deti hai
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    ========================================
    YEH HAI AUTH MIDDLEWARE
    ========================================

    Kaam: Har protected route ke liye user verify karna.
    Bina valid token ke koi protected route access nahi kar sakta.

    ⚡ Kaise kaam karta hai (step by step):

    [1] Jab koi route like GET /profile call hota hai:
        @app.get("/profile")
        def get_profile(user: User = Depends(get_current_user)):
            return user

    [2] FastAPI dekhta hai: "Arre, is route mein Depends(get_current_user) hai"
        To pehle get_current_user() function call karega.

    [3] get_current_user() ke 2 dependencies hain:
        a) credentials = Depends(security)
           -> HTTPBearer() request ka header check karega
           -> Header expected: "Authorization: Bearer eyJhbGci..."
           -> Agar header nahi hai -> 403 Forbidden auto
           -> Agar header hai -> token nikaal ke credentials.credentials mein daal dega

        b) db = Depends(get_db)
           -> Naya database session bana dega

    [4] Token verify karte hain verify_token() se:
        -> Decode hoga, signature check hoga, expiry check hogi
        -> Username nikal lega

    [5] Username se database mein user dhundein:
        -> db.query(User).filter(User.username == username).first()
        -> Agar user mila -> return user
        -> Agar nahi mila -> 404 error

    [6] get_current_user() ne user return kiya:
        -> Abhi route function chalega current_user ke saath
        -> Response bhej do

    📌 Agar kisi bhi step pe error aaya:
        -> HTTPException throw hoga
        -> Route function chalega hi nahi
        -> Client ko error response milega

    ========================================
    EXAMPLE: Complete Request Flow
    ========================================

    Request: GET /profile
    Header: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...

    1. FastAPI receives request
    2. Checks route: GET /profile -> get_profile()
    3. Sees Depends(get_current_user)
    4. Calls get_current_user():
       a) HTTPBearer() extracts token from header
       b) verify_token() checks token
       c) Queries DB for user
       d) Returns User object
    5. Passes User to get_profile(current_user)
    6. Returns User as JSON response
    """
    token = credentials.credentials  # HTTPBearer se token nikaalo

    # Token verify karo -> username milega
    result = verify_token(token)

    # verify_token returns {"username": "akhilesh"}
    username = result["username"]

    # Database mein username dhundo
    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User nahi mila",
        )

    return user
