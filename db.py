# db.py
import psycopg2
from psycopg2 import Error

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "KIM2",
    "user": "postgres",
    "password": "1111",   # ← ЗАМЕНИТЕ на свой пароль
}

_conn = None


def get_connection():
    """Возвращает соединение или None при ошибке."""
    global _conn
    try:
        if _conn is None or _conn.closed:
            _conn = psycopg2.connect(**DB_CONFIG)
            _conn.autocommit = False
        return _conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None


def execute(query, params=None, fetch=False):
    """Универсальный исполнитель SQL."""
    conn = get_connection()
    if conn is None:
        raise ConnectionError("Нет подключения к базе данных sportform.")
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            conn.commit()
            return cur.rowcount
    except Error:
        conn.rollback()
        raise