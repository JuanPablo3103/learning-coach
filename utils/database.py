import os
import psycopg2
from psycopg2.extras import RealDictCursor
import time

def get_connection():
    """Retorna una conexión a PostgreSQL"""
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    """Crea las tablas si no existen"""
    # Reintentar hasta que PostgreSQL esté listo
    retries = 5
    while retries > 0:
        try:
            conn = get_connection()
            break
        except Exception:
            retries -= 1
            time.sleep(2)
    
    if retries == 0:
        raise Exception("No se pudo conectar a PostgreSQL")

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(100) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            password VARCHAR(64) NOT NULL,
            email VARCHAR(200) NOT NULL,
            security_question TEXT,
            security_answer VARCHAR(64)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            username VARCHAR(100) PRIMARY KEY REFERENCES users(username),
            topic VARCHAR(200) NOT NULL,
            available_hours FLOAT NOT NULL,
            prior_knowledge TEXT NOT NULL,
            goals TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            username VARCHAR(100) PRIMARY KEY REFERENCES users(username),
            plan_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()