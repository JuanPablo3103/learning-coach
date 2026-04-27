 
import json
import os
import hashlib

USERS_FILE = "data/users.json"

def hash_password(password):
    """Convierte la contraseña en un hash seguro"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Carga los usuarios guardados"""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    """Guarda los usuarios en el archivo"""
    os.makedirs("data", exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, name, password, email):
    """Registra un usuario nuevo"""
    users = load_users()
    if username in users:
        return False, "El usuario ya existe"
    users[username] = {
        "name": name,
        "password": hash_password(password),
        "email": email
    }
    save_users(users)
    return True, "Usuario registrado exitosamente"

def login_user(username, password):
    """Verifica si el usuario y contraseña son correctos"""
    users = load_users()
    if username not in users:
        return False, "Usuario no encontrado"
    if users[username]["password"] != hash_password(password):
        return False, "Contraseña incorrecta"
    return True, users[username]["name"]

def get_user(username):
    """Obtiene los datos de un usuario"""
    users = load_users()
    return users.get(username, None)