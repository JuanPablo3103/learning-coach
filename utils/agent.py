import os
import json
import anthropic
from dotenv import load_dotenv
from utils.profile import get_profile
from utils.database import get_connection, log_agent_action

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_learning_plan(username):
    """Genera un plan de aprendizaje personalizado usando Claude"""

    profile = get_profile(username)
    if not profile:
        return None, "No se encontró el perfil del estudiante"

    log_agent_action(username, "generate_plan", f"Generando plan para tema: {profile['topic']}")

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
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        plan = json.loads(response_text)
        log_agent_action(username, "plan_generated", f"Plan generado exitosamente para: {profile['topic']}")
        return plan, "Plan generado exitosamente"

    except json.JSONDecodeError as e:
        log_agent_action(username, "plan_error", f"Error JSON: {str(e)}")
        return None, f"Error al procesar JSON: {str(e)}"
    except Exception as e:
        log_agent_action(username, "plan_error", f"Error: {str(e)}")
        return None, f"Error al generar el plan: {str(e)}"


def save_learning_plan(username, plan):
    """Guarda el plan en PostgreSQL"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO plans (username, plan_json)
            VALUES (%s, %s)
            ON CONFLICT (username) DO UPDATE SET
                plan_json = EXCLUDED.plan_json,
                created_at = CURRENT_TIMESTAMP
        """, (username, json.dumps(plan, ensure_ascii=False)))
        conn.commit()
        log_agent_action(username, "plan_saved", "Plan guardado en base de datos")
        return True
    except Exception as e:
        print(f"Error al guardar plan: {str(e)}")
        return False
    finally:
        cur.close()
        conn.close()


def load_learning_plan(username):
    """Carga el plan desde PostgreSQL"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT plan_json FROM plans WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])
    except Exception:
        return None
    finally:
        cur.close()
        conn.close()


def generate_quiz(username, topic, num_questions=5):
    """Genera preguntas de quiz sobre el tema del usuario usando Claude"""

    log_agent_action(username, "generate_quiz", f"Generando quiz sobre: {topic}")

    prompt = f"""
    Genera {num_questions} preguntas de opción múltiple sobre el tema: {topic}
    
    Cada pregunta debe tener 4 opciones (a, b, c, d) y una sola respuesta correcta.
    Dificultad: intermedia.
    
    Responde ÚNICAMENTE con este JSON sin texto adicional:
    {{
        "topic": "{topic}",
        "questions": [
            {{
                "question": "texto de la pregunta",
                "options": {{
                    "a": "opción a",
                    "b": "opción b",
                    "c": "opción c",
                    "d": "opción d"
                }},
                "correct": "a",
                "explanation": "explicación breve de por qué es correcta"
            }}
        ]
    }}
    """

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=3000,
            system="Eres un asistente que responde ÚNICAMENTE con JSON válido. Sin markdown, sin backticks, sin texto adicional.",
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        quiz = json.loads(response_text)
        log_agent_action(username, "quiz_generated", f"Quiz generado: {num_questions} preguntas sobre {topic}")
        return quiz, "Quiz generado exitosamente"

    except json.JSONDecodeError as e:
        log_agent_action(username, "quiz_error", f"Error JSON: {str(e)}")
        return None, f"Error al procesar quiz: {str(e)}"
    except Exception as e:
        log_agent_action(username, "quiz_error", f"Error: {str(e)}")
        return None, f"Error al generar quiz: {str(e)}"


def check_progress_alerts(username):
    """Revisa el progreso y retorna alertas si el usuario está atrasado o adelantado"""
    from utils.database import get_progress_stats, get_quiz_history

    stats = get_progress_stats(username)
    quiz_history = get_quiz_history(username)

    alerts = []

    if stats["total"] > 0:
        pct = stats["completed"] / stats["total"] * 100
        if pct == 0:
            alerts.append({
                "type": "warning",
                "message": "Aún no has completado ninguna tarea. ¡Empieza hoy!"
            })
        elif pct < 30:
            alerts.append({
                "type": "warning",
                "message": f"Solo has completado el {pct:.0f}% de tus tareas. ¡Puedes ponerte al día!"
            })
        elif pct >= 80:
            alerts.append({
                "type": "success",
                "message": f"¡Excelente! Has completado el {pct:.0f}% de tus tareas."
            })

    if quiz_history:
        last = quiz_history[0]
        score_pct = last["score"] / last["total"] * 100
        if score_pct < 50:
            alerts.append({
                "type": "warning",
                "message": f"Tu último quiz fue de {score_pct:.0f}%. Considera repasar el tema."
            })
        elif score_pct >= 80:
            alerts.append({
                "type": "success",
                "message": f"¡Muy bien! Sacaste {score_pct:.0f}% en tu último quiz."
            })

    log_agent_action(username, "check_alerts", f"Alertas generadas: {len(alerts)}")
    return alerts
def get_learning_stats(username):
    """Calcula estadísticas reales cruzando el plan con el progreso guardado"""
    from utils.database import get_task_progress

    plan = load_learning_plan(username)
    progress = get_task_progress(username)

    total = 0
    completed = 0
    per_week = {}

    if plan:
        for week in plan.get("weeks", []):
            w = week["week"]
            per_week.setdefault(w, {"total": 0, "completed": 0})
            for day in week.get("days", []):
                for idx, _res in enumerate(day.get("resources", [])):
                    total += 1
                    per_week[w]["total"] += 1
                    key = f"{w}-{day['day']}-{idx}"
                    if progress.get(key):
                        completed += 1
                        per_week[w]["completed"] += 1

    pct = round(completed / total * 100) if total else 0

    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "pct": pct,
        "per_week": per_week,
    }