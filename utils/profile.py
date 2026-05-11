from utils.database import get_connection

def get_profile(username):
    """Obtiene el perfil de un usuario"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT topic, available_hours, prior_knowledge, goals FROM profiles WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "topic": row[0],
            "available_hours": row[1],
            "prior_knowledge": row[2],
            "goals": row[3]
        }
    except Exception:
        return None
    finally:
        cur.close()
        conn.close()

def save_profile(username, topic, available_hours, prior_knowledge, goals):
    """Guarda o actualiza el perfil del estudiante"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO profiles (username, topic, available_hours, prior_knowledge, goals)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE SET
                topic = EXCLUDED.topic,
                available_hours = EXCLUDED.available_hours,
                prior_knowledge = EXCLUDED.prior_knowledge,
                goals = EXCLUDED.goals
        """, (username, topic, available_hours, prior_knowledge, goals))
        conn.commit()
        return True, "Perfil guardado exitosamente"
    except Exception as e:
        return False, f"Error al guardar perfil: {str(e)}"
    finally:
        cur.close()
        conn.close()

def profile_exists(username):
    """Verifica si el usuario ya tiene perfil"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM profiles WHERE username = %s", (username,))
        return cur.fetchone() is not None
    except Exception:
        return False
    finally:
        cur.close()
        conn.close()