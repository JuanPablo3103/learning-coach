import hashlib
from utils.database import get_connection, ph, is_sqlite

def hash_password(password):
    """Convierte la contraseña en un hash seguro"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user_with_security(username, name, password, email, security_question, security_answer):
    """Registra un usuario nuevo con pregunta de seguridad"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"SELECT username FROM users WHERE username = {p}", (username,))
        if cur.fetchone():
            return False, "El usuario ya existe"
        cur.execute(f"""
            INSERT INTO users (username, name, password, email, security_question, security_answer)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p})
        """, (username, name, hash_password(password), email, security_question, hash_password(security_answer.lower())))
        conn.commit()
        return True, "Usuario registrado exitosamente"
    except Exception as e:
        return False, f"Error al registrar: {str(e)}"
    finally:
        cur.close()
        conn.close()

def login_user(username, password):
    """Verifica si el usuario y contraseña son correctos"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"SELECT name, password FROM users WHERE username = {p}", (username,))
        row = cur.fetchone()
        if not row:
            return False, "Usuario no encontrado"
        if row[1] != hash_password(password):
            return False, "Contraseña incorrecta"
        return True, row[0]
    except Exception as e:
        return False, f"Error al iniciar sesión: {str(e)}"
    finally:
        cur.close()
        conn.close()

def get_user(username):
    """Obtiene los datos de un usuario"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"SELECT username, name, email, security_question FROM users WHERE username = {p}", (username,))
        row = cur.fetchone()
        if not row:
            return None
        return {"username": row[0], "name": row[1], "email": row[2], "security_question": row[3]}
    except Exception:
        return None
    finally:
        cur.close()
        conn.close()

def get_security_question(username):
    """Obtiene la pregunta de seguridad del usuario"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"SELECT security_question FROM users WHERE username = {p}", (username,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception:
        return None
    finally:
        cur.close()
        conn.close()

def verify_security_answer(username, answer):
    """Verifica la respuesta de seguridad"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"SELECT security_answer FROM users WHERE username = {p}", (username,))
        row = cur.fetchone()
        if not row:
            return False
        return row[0] == hash_password(answer.lower())
    except Exception:
        return False
    finally:
        cur.close()
        conn.close()

def update_password(username, new_password):
    """Actualiza la contraseña del usuario"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"UPDATE users SET password = {p} WHERE username = {p}", (hash_password(new_password), username))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        cur.close()
        conn.close()