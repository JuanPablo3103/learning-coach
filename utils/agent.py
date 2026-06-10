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
    from utils.database import get_quiz_history

    stats = get_learning_stats(username)
    quiz_history = get_quiz_history(username)

    alerts = []

    if stats["total"] > 0:
        pct = stats["pct"]
        if pct == 0:
            alerts.append({
                "type": "warning",
                "message": "Aún no has completado ninguna tarea. ¡Empieza hoy!"
            })
        elif pct < 30:
            alerts.append({
                "type": "warning",
                "message": f"Solo has completado el {pct}% de tus tareas. ¡Puedes ponerte al día!"
            })
        elif pct >= 80:
            alerts.append({
                "type": "success",
                "message": f"¡Excelente! Has completado el {pct}% de tus tareas."
            })

    if quiz_history:
        last = quiz_history[0]
        score_pct = round(last["score"] / last["total"] * 100) if last["total"] else 0
        if score_pct < 50:
            alerts.append({
                "type": "warning",
                "message": f"Tu último quiz fue de {score_pct}%. Considera repasar el tema."
            })
        elif score_pct >= 80:
            alerts.append({
                "type": "success",
                "message": f"¡Muy bien! Sacaste {score_pct}% en tu último quiz."
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
import streamlit as st
from utils.agent import generate_learning_plan, save_learning_plan, load_learning_plan

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")

    st.markdown("""
    <style>
        .block-container { max-width: 640px !important; padding-top: 2.5rem !important; }
        .stApp { background: #0F0E1A !important; }
        .plan-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 2rem; }
        .plan-logo-icon { width: 40px; height: 40px; border-radius: 10px; background: #534AB7; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .plan-logo-text { font-size: 16px; font-weight: 500; color: #E8E6F0; }
        .plan-logo-sub { font-size: 12px; color: rgba(255,255,255,0.35); }
        .plan-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .plan-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .meta-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 2rem; }
        .meta-card { background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 1rem; }
        .meta-label { font-size: 11px; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
        .meta-value { font-size: 15px; font-weight: 500; color: #E8E6F0; }
        .week-card { background: rgba(255,255,255,0.02); border: 0.5px solid rgba(255,255,255,0.07); border-radius: 12px; margin-bottom: 1rem; overflow: hidden; }
        .week-header { padding: 1rem 1.25rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 0.5px solid rgba(255,255,255,0.06); }
        .week-title { font-size: 15px; font-weight: 500; color: #E8E6F0; }
        .week-badge { background: rgba(83,74,183,0.2); border: 0.5px solid rgba(83,74,183,0.3); border-radius: 6px; padding: 3px 10px; font-size: 11px; color: #A9A3E8; }
        .week-objective { padding: 0.75rem 1.25rem; font-size: 13px; color: rgba(255,255,255,0.45); border-bottom: 0.5px solid rgba(255,255,255,0.06); }
        .day-card { padding: 1rem 1.25rem; border-bottom: 0.5px solid rgba(255,255,255,0.04); }
        .day-card:last-child { border-bottom: none; }
        .day-header { display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem; }
        .day-dot { width: 8px; height: 8px; border-radius: 50%; background: #534AB7; flex-shrink: 0; }
        .day-name { font-size: 13px; font-weight: 500; color: #A9A3E8; }
        .day-topic { font-size: 14px; color: #E8E6F0; margin-bottom: 0.4rem; }
        .day-duration { font-size: 12px; color: rgba(255,255,255,0.3); margin-bottom: 0.75rem; }
        .resource-link { display: flex; align-items: center; gap: 8px; padding: 7px 10px; background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.07); border-radius: 7px; margin-bottom: 6px; text-decoration: none; }
        .resource-icon { font-size: 14px; }
        .resource-title { font-size: 13px; color: #7F77DD; flex: 1; }
        .resource-duration { font-size: 11px; color: rgba(255,255,255,0.25); }
        .stButton > button {
            width: 100% !important; background: transparent !important;
            border: 0.5px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important; color: rgba(255,255,255,0.4) !important;
            font-size: 13px !important; margin-top: 0.5rem !important;
        }
        .stButton > button:hover {
            border-color: #534AB7 !important; color: #7F77DD !important;
        }
    </style>

    <div class="plan-logo">
        <div class="plan-logo-icon">🧠</div>
        <div>
            <div class="plan-logo-text">Learning Coach</div>
            <div class="plan-logo-sub">Tu coach de aprendizaje con IA</div>
        </div>
    </div>
    <div class="plan-title">📅 Mi Plan de Aprendizaje</div>
    <div class="plan-sub">Aquí está tu hoja de ruta personalizada generada por IA</div>
    """, unsafe_allow_html=True)

    existing_plan = load_learning_plan(username)

    if existing_plan and not st.session_state.get("generating"):
        show_plan(existing_plan)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Generar nuevo plan"):
            st.session_state.generating = True
            st.rerun()
    else:
        st.session_state.generating = True

    if st.session_state.get("generating"):
        generate_plan(username)

    if st.button("⬅️ Volver al dashboard"):
        st.session_state.generating = False
        st.session_state.page = "dashboard"
        st.rerun()


def generate_plan(username):
    st.info("🤖 El agente está generando tu plan personalizado...")
    with st.spinner("Analizando tu perfil y generando el plan..."):
        plan, message = generate_learning_plan(username)
    if plan:
        save_learning_plan(username, plan)
        st.session_state.generating = False
        st.success("✅ Plan generado exitosamente")
        st.rerun()
    else:
        st.error(f"❌ {message}")
        st.session_state.generating = False


def show_plan(plan):
    resource_icons = {
        "video": "🎬",
        "article": "📖",
        "course": "🎓",
        "book": "📚",
        "tutorial": "💻",
        "podcast": "🎧",
    }

    st.markdown(f"""
    <div class="meta-cards">
        <div class="meta-card">
            <div class="meta-label">Tema</div>
            <div class="meta-value">{plan['topic']}</div>
        </div>
        <div class="meta-card">
            <div class="meta-label">Duración</div>
            <div class="meta-value">{plan['duration_weeks']} semanas</div>
        </div>
        <div class="meta-card">
            <div class="meta-label">Horas / día</div>
            <div class="meta-value">{plan['weekly_hours']} horas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    full_html = ""

    for week in plan['weeks']:
        days_html = ""
        for day in week['days']:
            resources_html = ""
            for resource in day['resources']:
                icon = resource_icons.get(resource.get('type', ''), '🔗')
                resources_html += f"""<a class="resource-link" href="{resource['url']}" target="_blank"><span class="resource-icon">{icon}</span><span class="resource-title">{resource['title']}</span><span class="resource-duration">{resource['duration_minutes']} min</span></a>"""

            days_html += f"""<div class="day-card"><div class="day-header"><div class="day-dot"></div><div class="day-name">{day['day']}</div></div><div class="day-topic">{day['topic']}</div><div class="day-duration">⏰ {day['duration_hours']} horas</div>{resources_html}</div>"""

        full_html += f"""<div class="week-card"><div class="week-header"><div class="week-title">📅 Semana {week['week']} — {week['title']}</div><div class="week-badge">Semana {week['week']}</div></div><div class="week-objective">🎯 {week['objective']}</div>{days_html}</div>"""

    st.markdown(full_html, unsafe_allow_html=True)
def negotiate_plan(username, feedback):
    """Ajusta el plan existente según el feedback del estudiante, sin regenerarlo desde cero"""
    current_plan = load_learning_plan(username)
    if not current_plan:
        return None, "No tienes un plan para ajustar. Genera uno primero."

    log_agent_action(username, "negotiate_plan", f"Feedback: {feedback}")

    prompt = f"""
    Eres un coach de aprendizaje. El estudiante tiene este plan actual (en JSON):

    {json.dumps(current_plan, ensure_ascii=False)}

    El estudiante pide el siguiente cambio:
    "{feedback}"

    Ajusta el plan respetando esa petición (puedes cambiar temas, días, recursos, duración, etc.),
    pero MANTÉN exactamente la misma estructura JSON con las mismas claves.
    Conserva lo que el estudiante no pidió cambiar.

    Responde ÚNICAMENTE con el JSON del plan ajustado, sin texto adicional, con esta estructura:
    {{
        "topic": "...",
        "duration_weeks": 2,
        "weekly_hours": 1,
        "weeks": [
            {{
                "week": 1,
                "title": "...",
                "objective": "...",
                "days": [
                    {{
                        "day": "Lunes",
                        "topic": "...",
                        "duration_hours": 1,
                        "resources": [
                            {{"title": "...", "type": "video", "url": "https://...", "duration_minutes": 30}}
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

        new_plan = json.loads(response_text)
        log_agent_action(username, "plan_negotiated", "Plan ajustado según feedback del estudiante")
        return new_plan, "Plan ajustado exitosamente"

    except json.JSONDecodeError as e:
        log_agent_action(username, "negotiate_error", f"Error JSON: {str(e)}")
        return None, f"Error al procesar JSON: {str(e)}"
    except Exception as e:
        log_agent_action(username, "negotiate_error", f"Error: {str(e)}")
        return None, f"Error al ajustar el plan: {str(e)}"