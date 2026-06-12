# ============================================================
# models.py
# Kaam: SQLAlchemy ka User table model
# ============================================================
# Theory: ORM (Object Relational Mapping)
# Database table ko Python class ki tarah treat karo.
# Har class = ek table, har variable = ek column.

# ------------------------------------------------------------------
# from sqlalchemy import Column, Integer, String, Boolean, DateTime
# 📌 SQLAlchemy ke column types import kar rahe hain
#
# Column(table_column) -> ek field/database column represent karta hai
#   Jaise Column(Integer) ka matlab 'integer type ka column'
#
# Integer -> SQL ka INT (numbers) - jaise id, age
# String(n) -> SQL ka VARCHAR(n) - jaise username(50 chars)
# Boolean -> SQL ka BOOLEAN - jaise is_active (True/False)
# DateTime -> SQL ka TIMESTAMP - jaise created_at
# ------------------------------------------------------------------
from sqlalchemy import Column, Integer, String, Boolean, DateTime

# ------------------------------------------------------------------
# from datetime import datetime
# 📌 Python ka built-in datetime module
# 🔧 Kaam: datetime.utcnow() function jo CURRENT UTC time return karta hai
#    Iska use 'created_at' field ke default value ke liye hoga.
#    Jab bhi naya user register karega, automatically current time set ho jayega.
# ------------------------------------------------------------------
from datetime import datetime

# ------------------------------------------------------------------
# from app.database import Base
# 📌 database.py se 'Base' import kar rahe hain
# 🔧 Base = declarative_base() ka return value
# ❓ Kyun? User class ko Base ko extend karna hai taake SQLAlchemy
#    samjhe ki "yeh ek database table hai". Agar Base extend nahi karenge
#    to SQLAlchemy isse table nahi maanega.
# ------------------------------------------------------------------
from app.database import Base


class User(Base):
    """
    📌 users table ka ORM model

    🔗 database.py ke Base ko extend karta hai
       Iska matlab: SQLAlchemy is class ko ek table maanega

    ⚡ Har Column variable ek database column represent karta hai

    Table structure:
    ┌──────────────────┬──────────────┬──────────────────────────┐
    │ Column           │ Type         │ Description              │
    ├──────────────────┼──────────────┼──────────────────────────┤
    │ id               │ Integer      │ Unique ID (auto-incr.)   │
    │ username         │ String(50)   │ Unique, indexed          │
    │ email            │ String(100)  │ Unique, indexed          │
    │ hashed_password  │ String(255)  │ bcrypt hash             │
    │ full_name        │ String(100)  │ Optional                 │
    │ is_active        │ Boolean      │ Default True             │
    │ created_at       │ DateTime     │ Auto-set on register     │
    └──────────────────┴──────────────┴──────────────────────────┘
    """

    # __tablename__ = table ka naam jo database mein banega
    __tablename__ = "users"

    # Column(Integer, primary_key=True, index=True)
    # primary_key -> unique identifier, auto-increment
    # index -> fast search ke liye
    id = Column(Integer, primary_key=True, index=True)

    # String(50) -> VARCHAR(50) in SQL
    # unique=True -> koi do user ka username same nahi ho sakta
    # nullable=False -> yeh field mandatory hai (blank nahi ho sakti)
    # index=True -> SELECT jaldi se ho is field pe
    username = Column(String(50), unique=True, nullable=False, index=True)

    email = Column(String(100), unique=True, nullable=False, index=True)

    # hashed_password -> bcrypt algorithm se hash kiya hua password
    # plain text kabhi store nahi karte!
    hashed_password = Column(String(255), nullable=False)

    # nullable=True -> yeh optional field hai
    full_name = Column(String(100), nullable=True)

    # default=True -> jab naya user bane to automatically True set ho jayega
    is_active = Column(Boolean, default=True)

    # default=datetime.utcnow -> jab bhi naya row create ho, current time set ho
    # Note: datetime.utcnow hai, datetime.utcnow() nahi!
    # Difference: utcnow = function reference, utcnow() = call karna
    # Jab bhi naya record bane function call hoga
    created_at = Column(DateTime, default=datetime.utcnow)
