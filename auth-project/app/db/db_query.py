import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from app.db.database import get_connection

load_dotenv()


def query(sql, params=None, fetchone=False, fetchall=False, as_dict=False):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor) if as_dict else conn.cursor()

    try:
        cursor.execute(sql, params or ())

        result = None

        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            conn.commit()  # INSERT/UPDATE/DELETE
        return result

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
    conn.close()
