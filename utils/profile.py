import json
import os

PROFILES_FILE = "data/profiles.json"

def load_profiles():
    """Carga los perfiles guardados"""
    if not os.path.exists(PROFILES_FILE):
        return {}
    with open(PROFILES_FILE, "r") as f:
        return json.load(f)

def save_profiles(profiles):
    """Guarda los perfiles"""
    os.makedirs("data", exist_ok=True)
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

def get_profile(username):
    """Obtiene el perfil de un usuario"""
    profiles = load_profiles()
    return profiles.get(username, None)

def save_profile(username, topic, available_hours, prior_knowledge, goals):
    """Guarda o actualiza el perfil del estudiante"""
    profiles = load_profiles()
    profiles[username] = {
        "topic": topic,
        "available_hours": available_hours,
        "prior_knowledge": prior_knowledge,
        "goals": goals
    }
    save_profiles(profiles)
    return True, "Perfil guardado exitosamente"

def profile_exists(username):
    """Verifica si el usuario ya tiene perfil"""
    profiles = load_profiles()
    return username in profiles