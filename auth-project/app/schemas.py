# ============================================================
# schemas.py
# Kaam: Pydantic models - Request/Response data validation
# ============================================================
# Theory: Pydantic = FastAPI ka validation engine
# - Request aane par body ko validate karta hai
# - Response bhejne se pehle format check karta hai
# - SQLAlchemy model se Pydantic model mein convert karta hai

# ------------------------------------------------------------------
# from pydantic import BaseModel, field_validator
# 📌 pydantic = Python ka data validation library
#
# BaseModel -> Pydantic model ka parent class
#   🔧 Isko extend karte hi auto-validation, type checking, parsing
#      sab free mein milta hai. Jaise:
#      - username: str -> sirf string accept hoga
#      - Agar int diya to auto 400 error aayega
#
# field_validator -> decorator hai field-level validation ke liye
#   🔧 Jab bhi kisi field ki value set hoti hai, yeh turant check karta hai
#   Syntax: @field_validator("field_name") ke baad function likho
#   Example: @field_validator("email") -> email set hote hi validate ho jayega
# ------------------------------------------------------------------
from pydantic import BaseModel, field_validator

# ------------------------------------------------------------------
# from datetime import datetime
# 📌 Python built-in datetime module
# 🔧 UserResponse mein 'created_at: datetime' type hint ke liye
# ------------------------------------------------------------------
from datetime import datetime

# ------------------------------------------------------------------
# import re
# 📌 re = Regular Expression (regex) - pattern matching library
# 🔧 Kaam: Strings ka pattern check karna
#    re.match(pattern, string) -> check karta hai pattern match karta hai ya nahi
#    re.search(pattern, string) -> pattern string mein kahin bhi milta hai?
#
# Use cases in this file:
#   ^[a-zA-Z0-9_]{3,30}$ -> username format
#   ^[a-zA-Z0-9._%+-]+@... -> email format
#   [A-Z] -> password mein uppercase hai?
#   \d -> password mein digit hai?
# ------------------------------------------------------------------
import re


# ===================== VALIDATION HELPERS ======================

def validate_username(value: str) -> str:
    """
    Username validation rule:
    - 3 se 30 characters
    - Sirf letters (a-z, A-Z), digits (0-9), underscore (_)
    - Koi space ya special character nahi

    ^[a-zA-Z0-9_]{3,30}$
    ^ -> start of string
    $ -> end of string
    [a-zA-Z0-9_] -> in characters me se koi bhi
    {3,30} -> 3 se 30 baar repeat
    """
    if not re.match(r"^[a-zA-Z0-9_]{3,30}$", value):
        raise ValueError(
            "Username 3-30 characters, sirf letters, digits aur underscore allowed hai"
        )
    return value


def validate_email(value: str) -> str:
    """
    Email validation:
    Basic format: username@domain.com
    Regex explain:
    ^[a-zA-Z0-9._%+-]+  -> username part (letters, digits, ., _, %, +, -)
    @                    -> @ symbol
    [a-zA-Z0-9.-]+      -> domain name
    \\.[a-zA-Z]{2,}$    -> dot + extension like com, org (2+ letters)
    """
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
        raise ValueError("Email sahi format mein nahi hai (example@domain.com)")
    return value.lower()  # Normalize: hamesha lowercase mein store karo


def validate_password_strength(value: str) -> str:
    """
    Password strength rules:
    1. Kam se kam 8 characters
    2. Ek uppercase letter (A-Z)
    3. Ek lowercase letter (a-z)
    4. Ek digit (0-9)
    5. Ek special character (!@#$% etc.)
    """
    if len(value) < 8:
        raise ValueError("Password kam se kam 8 characters ka hona chahiye")
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password mein ek uppercase letter hona chahiye (A-Z)")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password mein ek lowercase letter hona chahiye (a-z)")
    if not re.search(r"\d", value):
        raise ValueError("Password mein ek digit hona chahiye (0-9)")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", value):
        raise ValueError("Password mein ek special character hona chahiye (!@#$%^&* etc)")
    return value


# ===================== REQUEST SCHEMAS ========================
# Ye classes define karti hain ki client kya data bhejega

class UserRegister(BaseModel):
    """
    📌 POST /register ka request body format

    FastAPI automatically:
    1. Request body parse karega
    2. Har field ka type check karega
    3. field_validator ke hisaab se validate karega
    4. Agar kuch galat hai -> 422 Validation Error
    """
    username: str           # Required - user ka naam
    email: str              # Required - email address
    password: str           # Required - password
    confirm_password: str   # Required - password dobara (match check)
    full_name: str | None = None  # Optional - poora naam

    # @field_validator decorator ka kaam:
    # Jab bhi 'username' field set hogi, pehle yeh function chalega
    # Agar validate_username error throw karega to request reject ho jayegi
    @field_validator("username")
    @classmethod
    def validate_username_field(cls, value):
        return validate_username(value)

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, value):
        return validate_email(value)

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, value):
        return validate_password_strength(value)


class UserLogin(BaseModel):
    """
    📌 POST /login ka request body format
    Sirf username aur password chahiye login ke liye
    """
    username: str
    password: str


# ===================== RESPONSE SCHEMAS =======================
# Ye classes define karti hain ki server kya response bhejega
# DHYAN: Response mein kabhi password mat bhejo!

class UserResponse(BaseModel):
    """
    📌 Response format jab bhi user data bhejna ho

    from_attributes = True:
    SQLAlchemy model (User) ko Pydantic model (UserResponse) mein
    auto-convert karne ke liye. Iske bina manually field map karna
    padta.
    """
    id: int
    username: str
    email: str
    full_name: str | None = None
    is_active: bool
    created_at: datetime

    # model_config = Pydantic v2 ka tarika configuration dene ka
    # from_attributes = True means SQLAlchemy model se data lo
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    📌 POST /login success response
    JWT access token + user data ek saath bhejta hai
    """
    access_token: str           # JWT token string
    token_type: str = "bearer"  # Token type (hamesha bearer)
    user: UserResponse          # User ka data bhi saath mein
