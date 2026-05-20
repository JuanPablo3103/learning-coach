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