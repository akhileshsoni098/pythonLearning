# ============================================================
# database.py
# Kaam: PostgreSQL connection, session, aur auto database create
# ============================================================

# ------------------------------------------------------------------
# import psycopg2
# 📌 psycopg2 = Python ka PostgreSQL driver (direct connection)
# 🔧 Kaam: SQLAlchemy ke alawa, hume direct PostgreSQL se connect
#    karna padta hai sirf DATABASE CREATE karne ke liye.
# ❌ Kyunki SQLAlchemy ka create_all() sirf TABLES bana sakta hai,
#    DATABASE nahi bana sakta. Isliye psycopg2 use karte hain.
# ------------------------------------------------------------------
import psycopg2

# ------------------------------------------------------------------
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# 📌 ISOLATION_LEVEL_AUTOCOMMIT = har query turant execute karo
# 🔧 Kaam: CREATE DATABASE command ko transaction ke bahar run karna
#    padta hai. Agar transaction ke andar karenge to PostgreSQL error
#    dega. Isliye AUTOCOMMIT mode set karte hain.
# ------------------------------------------------------------------
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ------------------------------------------------------------------
# from sqlalchemy import create_engine
# 📌 create_engine = SQLAlchemy ka connection manager
# 🔧 Kaam: Database URL de do, yeh connection pool banata hai.
#    Pool = multiple connections ready rehtin hain. Jab jaroorat ho
#    turant ek connection mil jata hai.
# ------------------------------------------------------------------
from sqlalchemy import create_engine

# ------------------------------------------------------------------
# from sqlalchemy.orm import sessionmaker, declarative_base
# 📌 sessionmaker -> DB session banane ka factory function
# 📌 declarative_base -> Table models ke liye parent class
# 🔧 sessionmaker: Har HTTP request ke liye ek naya session deta hai
#    (jaise ek call center agent ek customer ke saath baat kare)
# 🔧 declarative_base: Isko class extend karegi to SQLAlchemy samjhega
#    ki "yeh class ek database table hai"
# ------------------------------------------------------------------
from sqlalchemy.orm import sessionmaker, declarative_base


# ===================== DATABASE URL ============================
# Yeh hai connection string. Format:
# postgresql://username:password@host:port/database_name
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/python_auth_db"


# ===================== DATABASE AUTO-CREATE ====================
def ensure_database_exists():
    """
    Kaam: Check karta hai 'python_auth_db' exist karta hai ya nahi.
          Agar nahi hai to create kar deta hai.

    Kyun zaroori hai?
    - SQLAlchemy ka create_all() sirf TABLES create karta hai.
    - DATABASE khud nahi bana sakta. To pehle manually banana padega.

    Kaise kaam karta hai:
    1. 'postgres' database se connect karo (yeh default DB hota hai)
    2. pg_database system table mein check karo
    3. Agar nahi mila to CREATE DATABASE command chalao
    """
    db_name = "python_auth_db"
    # 'postgres' database se connect - yeh har PostgreSQL mein default milta hai
    default_url = "postgresql://postgres:12345678@localhost:5432/postgres"

    try:
        # psycopg2.connect() -> PostgreSQL se connection kholta hai
        conn = psycopg2.connect(default_url)

        # AUTOCOMMIT mode: har query immediately execute karo
        # CREATE DATABASE ko transaction mein nahi chal sakte
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # pg_database = system table jisme saari databases ki list hai
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()  # fetchone() -> ek row return karega ya None

        if not exists:
            # Database create karo - double quotes IMPORTANT hai!
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"[OK] Database '{db_name}' create kar diya gaya!")
        else:
            print(f"[OK] Database '{db_name}' pehle se exist karta hai")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[WARN] Database check/create karte time issue: {e}")
        print("  -> Shayad DB pehle se exist karta hai, aage badh rahe hain...")


# ===================== SQLALCHEMY ENGINE =======================
# create_engine() ko DATABASE_URL do
# Yeh internally connection pool banata hai
# Pool size by default = 5 connections
engine = create_engine(DATABASE_URL)

# sessionmaker() -> naye session banane ka factory
# autocommit=False -> commit() manually call karna padega
# autoflush=False -> flush bhi manually hoga (recommended)
# bind=engine -> kiska engine use karna hai
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# declarative_base() -> parent class jo table models create karega
# Isko extend karne wali har class ek database table ban jayegi
Base = declarative_base()


# ===================== DB SESSION DEPENDENCY ===================
def get_db():
    """
    FastAPI dependency: har request ke liye naya DB session
    'yield' ka matlab hai:
    - Jab tak request chale, tab tak session active
    - Request khatam hote hi 'finally' block mein session.close()

    Ye function 'Depends(get_db)' ke saath route mein use hota hai
    """
    db = SessionLocal()  # Naya session banao
    try:
        yield db  # Session ko route ko de do
    finally:
        db.close()  # Route khatam -> session band karo
