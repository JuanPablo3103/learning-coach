import os
import psycopg2
from psycopg2.extras import RealDictCursor
import time

def get_connection():
    """Retorna una conexión a PostgreSQL"""
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    """Crea las tablas si no existen"""
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

    # NUEVO: progreso de tareas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_progress (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) REFERENCES users(username),
            week_number INTEGER NOT NULL,
            day_name VARCHAR(100) NOT NULL,
            resource_index INTEGER NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            UNIQUE(username, week_number, day_name, resource_index)
        )
    """)

    # NUEVO: historial de quizzes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_history (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) REFERENCES users(username),
            topic VARCHAR(200) NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # NUEVO: log de decisiones del agente
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) REFERENCES users(username),
            action VARCHAR(100) NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migración: ampliar day_name por si la tabla ya existía con VARCHAR(20)
    cur.execute("ALTER TABLE task_progress ALTER COLUMN day_name TYPE VARCHAR(100)")
    conn.commit()
    cur.close()
    conn.close()


# ─── Task progress ─────────────────────────────────────────────────────────

def mark_task(username, week_number, day_name, resource_index, completed):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if completed:
            cur.execute("""
                INSERT INTO task_progress (username, week_number, day_name, resource_index, completed, completed_at)
                VALUES (%s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
                ON CONFLICT (username, week_number, day_name, resource_index)
                DO UPDATE SET completed = TRUE, completed_at = CURRENT_TIMESTAMP
            """, (username, week_number, day_name, resource_index))
        else:
            cur.execute("""
                INSERT INTO task_progress (username, week_number, day_name, resource_index, completed)
                VALUES (%s, %s, %s, %s, FALSE)
                ON CONFLICT (username, week_number, day_name, resource_index)
                DO UPDATE SET completed = FALSE, completed_at = NULL
            """, (username, week_number, day_name, resource_index))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_task_progress(username):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT week_number, day_name, resource_index, completed
            FROM task_progress WHERE username = %s
        """, (username,))
        rows = cur.fetchall()
        return {
            f"{r['week_number']}-{r['day_name']}-{r['resource_index']}": r['completed']
            for r in rows
        }
    finally:
        cur.close()
        conn.close()


def get_progress_stats(username):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE completed = TRUE) AS completed,
                COUNT(*) AS total
            FROM task_progress WHERE username = %s
        """, (username,))
        row = cur.fetchone()
        return {
            "completed": row["completed"] or 0,
            "total": row["total"] or 0
        }
    finally:
        cur.close()
        conn.close()


# ─── Quiz history ──────────────────────────────────────────────────────────

def save_quiz_result(username, topic, score, total):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO quiz_history (username, topic, score, total)
            VALUES (%s, %s, %s, %s)
        """, (username, topic, score, total))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_quiz_history(username):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT topic, score, total, taken_at
            FROM quiz_history WHERE username = %s
            ORDER BY taken_at DESC LIMIT 20
        """, (username,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


# ─── Agent logs ────────────────────────────────────────────────────────────

def log_agent_action(username, action, details=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO agent_logs (username, action, details)
            VALUES (%s, %s, %s)
        """, (username, action, details))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_agent_logs(username, limit=30):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT action, details, created_at
            FROM agent_logs WHERE username = %s
            ORDER BY created_at DESC LIMIT %s
        """, (username, limit))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()