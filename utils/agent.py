import os
import json
import anthropic
from dotenv import load_dotenv
from utils.profile import get_profile

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_learning_plan(username):
    """Genera un plan de aprendizaje personalizado usando Claude"""
    
    profile = get_profile(username)
    if not profile:
        return None, "No se encontró el perfil del estudiante"

    prompt = f"""
    Eres un coach de aprendizaje experto. Genera un plan de aprendizaje semanal personalizado.
    
    Información del estudiante:
    - Tema: {profile['topic']}
    - Horas por día: {profile['available_hours']}
    - Nivel: {profile['prior_knowledge']}
    - Objetivo: {profile['goals']}
    
    Genera un plan de 2 semanas, con SOLO 3 días por semana (Lunes, Miércoles, Viernes).
    Cada día tiene SOLO 2 recursos máximo.
    
    Responde ÚNICAMENTE con este JSON exacto sin texto adicional:
    {{
        "topic": "{profile['topic']}",
        "duration_weeks": 2,
        "weekly_hours": {profile['available_hours']},
        "weeks": [
            {{
                "week": 1,
                "title": "título semana 1",
                "objective": "objetivo semana 1",
                "days": [
                    {{
                        "day": "Lunes",
                        "topic": "tema del día",
                        "duration_hours": {profile['available_hours']},
                        "resources": [
                            {{
                                "title": "título recurso",
                                "type": "video",
                                "url": "https://ejemplo.com",
                                "duration_minutes": 30
                            }}
                        ]
                    }}
                ]
            }}
        ]
    }}
    """

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=8000,
            system="Eres un asistente que responde ÚNICAMENTE con JSON válido. Sin markdown, sin backticks, sin texto adicional.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        # Limpiar posibles backticks
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        plan = json.loads(response_text)
        return plan, "Plan generado exitosamente"
    
    except json.JSONDecodeError as e:
        return None, f"Error al procesar JSON: {str(e)}"
    except Exception as e:
        return None, f"Error al generar el plan: {str(e)}"

def save_learning_plan(username, plan):
    """Guarda el plan de aprendizaje"""
    os.makedirs("data", exist_ok=True)
    plans_file = "data/plans.json"
    
    if os.path.exists(plans_file):
        with open(plans_file, "r") as f:
            plans = json.load(f)
    else:
        plans = {}
    
    plans[username] = plan
    
    with open(plans_file, "w") as f:
        json.dump(plans, f, indent=4, ensure_ascii=False)

def load_learning_plan(username):
    """Carga el plan de aprendizaje del usuario"""
    plans_file = "data/plans.json"
    if not os.path.exists(plans_file):
        return None
    with open(plans_file, "r") as f:
        plans = json.load(f)
    return plans.get(username, None)