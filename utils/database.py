import os
import time
import sqlite3

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def get_connection():
    """Retorna una conexión a PostgreSQL o SQLite (fallback)."""
    db_url = os.getenv("DATABASE_URL")
    if db_url and PSYCOPG2_AVAILABLE:
        return psycopg2.connect(db_url)
    # Fallback to SQLite in the project directory
    conn = sqlite3.connect(
        os.path.join(os.path.dirname(__file__), "learning_coach.db"),
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def is_sqlite():
    """Retorna True si estamos usando SQLite (modo local/fallback)."""
    return not (os.getenv("DATABASE_URL") and PSYCOPG2_AVAILABLE)


def ph():
    """Retorna el placeholder de parámetro adecuado para la DB activa."""
    return "?" if is_sqlite() else "%s"


def init_db():
    """Crea las tablas si no existen, con soporte para PostgreSQL y SQLite."""
    # Reintentar hasta que la base de datos esté lista (solo aplica a PostgreSQL)
    retries = 5
    while retries > 0:
        try:
            conn = get_connection()
            break
        except Exception as e:
            retries -= 1
            if retries == 0:
                raise Exception(f"No se pudo conectar a la base de datos: {e}")
            time.sleep(2)
    
    cur = conn.cursor()
    # Compatibilidad con la sintaxis de SQLite (usa ? placeholder y tipos genéricos)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            security_question TEXT,
            security_answer TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            available_hours REAL NOT NULL,
            prior_knowledge TEXT NOT NULL,
            goals TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            username TEXT PRIMARY KEY,
            plan_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            week INTEGER NOT NULL,
            day TEXT NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            answers_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            week INTEGER NOT NULL,
            day TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS decision_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()