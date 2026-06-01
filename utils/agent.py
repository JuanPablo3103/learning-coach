import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from utils.profile import get_profile
from utils.database import get_connection, ph, is_sqlite

load_dotenv()

# ---------- Anthropic client (optional) ----------
try:
    import anthropic
    _api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=_api_key) if _api_key else None
except Exception:
    client = None

AI_AVAILABLE = client is not None


# ===================================================================
#  PLAN GENERATION
# ===================================================================

def _fallback_plan(profile):
    """Genera un plan de ejemplo cuando no hay API key de Anthropic."""
    topic = profile["topic"]
    hours = profile["available_hours"]
    level = profile["prior_knowledge"]

    weeks = []
    subtopics_w1 = [
        f"Introducción a {topic}",
        f"Conceptos fundamentales de {topic}",
        f"Herramientas básicas de {topic}",
    ]
    subtopics_w2 = [
        f"Práctica intermedia de {topic}",
        f"Proyecto aplicado de {topic}",
        f"Revisión y consolidación de {topic}",
    ]

    for w_idx, subtopics in enumerate([subtopics_w1, subtopics_w2], 1):
        days = []
        for d_idx, (day_name, sub) in enumerate(
            zip(["Lunes", "Miércoles", "Viernes"], subtopics)
        ):
            days.append({
                "day": day_name,
                "topic": sub,
                "duration_hours": hours,
                "resources": [
                    {
                        "title": f"Video: {sub}",
                        "type": "video",
                        "url": f"https://www.youtube.com/results?search_query={sub.replace(' ', '+')}",
                        "duration_minutes": 30,
                    },
                    {
                        "title": f"Artículo: {sub}",
                        "type": "article",
                        "url": f"https://www.google.com/search?q={sub.replace(' ', '+')}",
                        "duration_minutes": 20,
                    },
                ],
            })
        weeks.append({
            "week": w_idx,
            "title": f"Semana {w_idx} – {'Fundamentos' if w_idx == 1 else 'Aplicación'}",
            "objective": f"Dominar {'los fundamentos' if w_idx == 1 else 'la práctica'} de {topic}",
            "days": days,
        })

    return {
        "topic": topic,
        "duration_weeks": 2,
        "weekly_hours": hours,
        "weeks": weeks,
    }


def generate_learning_plan(username):
    """Genera un plan de aprendizaje personalizado usando Claude o fallback."""
    profile = get_profile(username)
    if not profile:
        return None, "No se encontró el perfil del estudiante"

    # ---- Fallback mode ----
    if not AI_AVAILABLE:
        plan = _fallback_plan(profile)
        return plan, "Plan generado en modo local (sin API key)"

    # ---- AI mode ----
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
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            system="Eres un asistente que responde ÚNICAMENTE con JSON válido. Sin markdown, sin backticks, sin texto adicional.",
            messages=[{"role": "user", "content": prompt}],
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
        return plan, "Plan generado exitosamente"

    except json.JSONDecodeError as e:
        return None, f"Error al procesar JSON: {str(e)}"
    except Exception as e:
        # Fallback on any API error
        plan = _fallback_plan(profile)
        return plan, f"Plan generado en modo fallback (error API: {str(e)[:60]})"


# ===================================================================
#  SAVE / LOAD PLAN  (SQLite-compatible)
# ===================================================================

def save_learning_plan(username, plan):
    """Guarda el plan de aprendizaje."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        if is_sqlite():
            cur.execute(f"""
                INSERT INTO plans (username, plan_json)
                VALUES ({p}, {p})
                ON CONFLICT(username) DO UPDATE SET
                    plan_json = excluded.plan_json,
                    created_at = CURRENT_TIMESTAMP
            """, (username, json.dumps(plan, ensure_ascii=False)))
        else:
            cur.execute(f"""
                INSERT INTO plans (username, plan_json)
                VALUES ({p}, {p})
                ON CONFLICT (username) DO UPDATE SET
                    plan_json = EXCLUDED.plan_json,
                    created_at = CURRENT_TIMESTAMP
            """, (username, json.dumps(plan, ensure_ascii=False)))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al guardar plan: {str(e)}")
        return False
    finally:
        cur.close()
        conn.close()


def load_learning_plan(username):
    """Carga el plan de aprendizaje."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"SELECT plan_json FROM plans WHERE username = {p}", (username,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])
    except Exception:
        return None
    finally:
        cur.close()
        conn.close()


# ===================================================================
#  QUIZ GENERATION (fallback + AI)
# ===================================================================

def _fallback_quiz(topic, day_topic):
    """Genera un quiz de ejemplo cuando no hay API key."""
    questions = [
        {
            "type": "multiple_choice",
            "question": f"¿Cuál es el concepto principal de '{day_topic}'?",
            "options": [
                f"Es una técnica avanzada de {topic}",
                f"Es un fundamento básico de {topic}",
                f"No tiene relación con {topic}",
                f"Es solo una herramienta de {topic}",
            ],
            "correct": 1,
        },
        {
            "type": "multiple_choice",
            "question": f"¿Qué beneficio principal ofrece aprender '{day_topic}'?",
            "options": [
                "Ningún beneficio práctico",
                f"Mejora la comprensión general de {topic}",
                "Solo es útil en teoría",
                "Es un requisito obligatorio",
            ],
            "correct": 1,
        },
        {
            "type": "multiple_choice",
            "question": f"¿Cuál es el mejor enfoque para estudiar '{day_topic}'?",
            "options": [
                "Solo leer resúmenes",
                "Memorizar sin entender",
                "Practicar con ejercicios y aplicar conceptos",
                "No es necesario estudiar",
            ],
            "correct": 2,
        },
        {
            "type": "true_false",
            "question": f"'{day_topic}' es un tema importante dentro de {topic}.",
            "correct": True,
        },
        {
            "type": "true_false",
            "question": f"No es necesario practicar para dominar '{day_topic}'.",
            "correct": False,
        },
    ]
    random.shuffle(questions)
    return questions


def generate_quiz(topic, day_topic):
    """Genera un quiz de 5 preguntas (3 opción múltiple + 2 V/F)."""
    if not AI_AVAILABLE:
        return _fallback_quiz(topic, day_topic), "Quiz generado en modo local"

    prompt = f"""
    Genera un quiz de evaluación sobre el siguiente tema de estudio.
    
    Tema general: {topic}
    Tema específico del día: {day_topic}
    
    Genera exactamente 5 preguntas:
    - 3 de opción múltiple (4 opciones cada una)
    - 2 de verdadero/falso
    
    Responde ÚNICAMENTE con este JSON:
    [
        {{
            "type": "multiple_choice",
            "question": "pregunta aquí",
            "options": ["opción A", "opción B", "opción C", "opción D"],
            "correct": 0
        }},
        {{
            "type": "true_false",
            "question": "afirmación aquí",
            "correct": true
        }}
    ]
    El campo "correct" para multiple_choice es el índice (0-3). Para true_false es true/false.
    """

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system="Responde ÚNICAMENTE con JSON válido.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        questions = json.loads(text.strip())
        return questions, "Quiz generado con IA"
    except Exception as e:
        return _fallback_quiz(topic, day_topic), f"Quiz fallback (error: {str(e)[:50]})"


# ===================================================================
#  QUIZ RESULTS
# ===================================================================

def save_quiz_result(username, week, day, topic, score, total, answers):
    """Guarda el resultado del quiz en la BD."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"""
            INSERT INTO quiz_results (username, week, day, topic, score, total, answers_json)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})
        """, (username, week, day, topic, score, total, json.dumps(answers, ensure_ascii=False)))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error guardando quiz: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def get_quiz_results(username):
    """Obtiene todos los resultados de quizzes del usuario."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"""
            SELECT week, day, topic, score, total, created_at
            FROM quiz_results WHERE username = {p}
            ORDER BY created_at DESC
        """, (username,))
        rows = cur.fetchall()
        return [
            {"week": r[0], "day": r[1], "topic": r[2], "score": r[3], "total": r[4], "created_at": r[5]}
            for r in rows
        ]
    except Exception:
        return []
    finally:
        cur.close()
        conn.close()


# ===================================================================
#  TASK PROGRESS
# ===================================================================

def mark_task_completed(username, week, day):
    """Marca una tarea como completada."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        # Check if already exists
        cur.execute(f"SELECT id FROM task_progress WHERE username={p} AND week={p} AND day={p}", (username, week, day))
        if cur.fetchone():
            cur.execute(f"UPDATE task_progress SET completed=1, completed_at=CURRENT_TIMESTAMP WHERE username={p} AND week={p} AND day={p}", (username, week, day))
        else:
            cur.execute(f"""
                INSERT INTO task_progress (username, week, day, completed, completed_at)
                VALUES ({p}, {p}, {p}, 1, CURRENT_TIMESTAMP)
            """, (username, week, day))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error marking task: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def get_task_progress(username):
    """Obtiene el progreso de tareas del usuario."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"SELECT week, day, completed FROM task_progress WHERE username = {p}", (username,))
        rows = cur.fetchall()
        return {f"{r[0]}-{r[1]}": bool(r[2]) for r in rows}
    except Exception:
        return {}
    finally:
        cur.close()
        conn.close()


# ===================================================================
#  ALERTS / DECISION HISTORY
# ===================================================================

def check_progress_alerts(username):
    """
    Compara progreso real vs esperado y genera alertas.
    Retorna una lista de alertas (puede estar vacía).
    """
    plan = load_learning_plan(username)
    if not plan:
        return []

    progress = get_task_progress(username)
    total_tasks = 0
    completed_tasks = 0

    for week in plan.get("weeks", []):
        for day in week.get("days", []):
            total_tasks += 1
            key = f"{week['week']}-{day['day']}"
            if progress.get(key):
                completed_tasks += 1

    if total_tasks == 0:
        return []

    # Calculate expected progress based on current date vs plan start
    # Simplified: use ratio of completed vs total
    completion_pct = completed_tasks / total_tasks
    # Assume linear expected progress: e.g. 50% by mid-plan
    expected_pct = 0.5  # simplificado

    alerts = []
    diff = completion_pct - expected_pct

    if diff <= -0.2:
        alerts.append({
            "type": "behind",
            "icon": "🔴",
            "message": f"Estás atrasado: has completado {completed_tasks}/{total_tasks} tareas ({completion_pct:.0%}). Se esperaba al menos {expected_pct:.0%}.",
            "action": "Considera dedicar más tiempo esta semana para ponerte al día.",
        })
    elif diff >= 0.2:
        alerts.append({
            "type": "ahead",
            "icon": "🟢",
            "message": f"¡Vas adelantado! Has completado {completed_tasks}/{total_tasks} tareas ({completion_pct:.0%}).",
            "action": "¡Excelente ritmo! Puedes profundizar en los temas o avanzar al siguiente nivel.",
        })
    else:
        alerts.append({
            "type": "on_track",
            "icon": "🟡",
            "message": f"Vas en buen ritmo: {completed_tasks}/{total_tasks} tareas completadas ({completion_pct:.0%}).",
            "action": "Sigue así, estás en camino de cumplir tu plan.",
        })

    return alerts


def log_decision(username, event_type, message, reason=""):
    """Registra un evento en el historial de decisiones."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"""
            INSERT INTO decision_history (username, event_type, message, reason)
            VALUES ({p}, {p}, {p}, {p})
        """, (username, event_type, message, reason))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging decision: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def get_decision_history(username):
    """Obtiene el historial de decisiones del usuario."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        p = ph()
        cur.execute(f"""
            SELECT event_type, message, reason, created_at
            FROM decision_history WHERE username = {p}
            ORDER BY created_at DESC LIMIT 50
        """, (username,))
        rows = cur.fetchall()
        return [
            {"event_type": r[0], "message": r[1], "reason": r[2], "created_at": r[3]}
            for r in rows
        ]
    except Exception:
        return []
    finally:
        cur.close()
        conn.close()