import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME
    )


def create_database():
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            database="postgres",
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))
            )
            print("Database created")
        else:
            print("Database already exists")

    except Exception as e:
        print("Error creating database:", e)

    finally:
        if cursor:
            cursor.close()
            if conn:
                conn.close()


def create_tables():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.autocommit = True
        cursor = conn.cursor()

        base_dir = os.path.dirname(__file__)
        schemas_dir = os.path.join(base_dir, "schemas")

        sql_files = sorted([f for f in os.listdir(schemas_dir) if f.endswith(".sql")])

        for file_name in sql_files:
            file_path = os.path.join(schemas_dir, file_name)

            with open(file_path, "r", encoding="utf-8") as f:
                sql_script = f.read()

                cursor.execute(sql_script)
                print(f"{file_name} executed")

    except Exception as e:
        print("Error creating tables:", e)

    finally:
        if cursor:
            cursor.close()
            if conn:
                conn.close()
