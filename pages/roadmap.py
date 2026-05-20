import streamlit as st
from utils.agent import load_learning_plan, generate_learning_plan, save_learning_plan

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")
    plan = load_learning_plan(username)

    st.markdown("""
    <style>
        .block-container { max-width: 620px !important; padding-top: 2.5rem !important; }
        .stApp { background: #0F0E1A !important; }
        .rm-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 2rem; }
        .rm-logo-icon { width: 40px; height: 40px; border-radius: 10px; background: #534AB7; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .rm-logo-text { font-size: 16px; font-weight: 500; color: #E8E6F0; }
        .rm-logo-sub { font-size: 12px; color: rgba(255,255,255,0.35); }
        .rm-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .rm-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .topic-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(83,74,183,0.2); border: 0.5px solid rgba(83,74,183,0.3); border-radius: 99px; padding: 6px 16px; font-size: 13px; color: #A9A3E8; margin-bottom: 2.5rem; }
        .timeline { position: relative; padding-left: 2rem; }
        .timeline::before { content: ''; position: absolute; left: 10px; top: 0; bottom: 0; width: 1.5px; background: linear-gradient(to bottom, #534AB7, rgba(83,74,183,0.1)); }
        .week-block { position: relative; margin-bottom: 2rem; }
        .week-dot { position: absolute; left: -2rem; top: 4px; width: 20px; height: 20px; border-radius: 50%; background: #534AB7; border: 2px solid #0F0E1A; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; color: #EEEDFE; z-index: 1; }
        .week-label { font-size: 11px; color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px; }
        .week-title { font-size: 15px; font-weight: 500; color: #E8E6F0; margin-bottom: 6px; }
        .week-objective { font-size: 13px; color: rgba(255,255,255,0.4); margin-bottom: 10px; }
        .days-row { display: flex; gap: 8px; flex-wrap: wrap; }
        .day-chip { background: rgba(255,255,255,0.04); border: 0.5px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 6px 12px; font-size: 12px; color: rgba(255,255,255,0.5); }
        .day-chip-day { color: #A9A3E8; font-weight: 500; }
        .next-card { position: relative; margin-top: 1rem; background: rgba(83,74,183,0.08); border: 0.5px solid rgba(83,74,183,0.2); border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1rem; }
        .next-title { font-size: 15px; font-weight: 500; color: #E8E6F0; margin-bottom: 6px; }
        .next-sub { font-size: 13px; color: rgba(255,255,255,0.4); margin-bottom: 1rem; }
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

    <div class="rm-logo">
        <div class="rm-logo-icon">🧠</div>
        <div>
            <div class="rm-logo-text">Learning Coach</div>
            <div class="rm-logo-sub">Tu coach de aprendizaje con IA</div>
        </div>
    </div>
    <div class="rm-title">🗺️ Tu Hoja de Ruta</div>
    <div class="rm-sub">Aquí está tu camino de aprendizaje personalizado</div>
    """, unsafe_allow_html=True)

    if not plan:
        st.warning("Aún no tienes un plan generado. Ve a Mi Plan para crear uno.")
        if st.button("📅 Ir a Mi Plan"):
            st.session_state.page = "plan"
            st.rerun()
    else:
        st.markdown(f'<div class="topic-badge">⚙️ {plan["topic"]} · {plan["duration_weeks"]} semanas · {plan["weekly_hours"]} horas/día</div>', unsafe_allow_html=True)

        full_html = "<div class='timeline'>"
        for week in plan['weeks']:
            days_html = ""
            for day in week['days']:
                days_html += f"""<div class="day-chip"><span class="day-chip-day">{day['day']}</span> — {day['topic']}</div>"""

            full_html += f"""<div class="week-block"><div class="week-dot">{week['week']}</div><div class="week-label">Semana {week['week']}</div><div class="week-title">{week['title']}</div><div class="week-objective">{week['objective']}</div><div class="days-row">{days_html}</div></div>"""

        full_html += """<div class="next-card"><div class="next-title">🚀 ¿Listo para el siguiente nivel?</div><div class="next-sub">Completaste tu plan actual. Genera un nuevo plan más avanzado y sigue creciendo.</div></div></div>"""

        st.markdown(full_html, unsafe_allow_html=True)

        if st.button("✨ Generar nuevo plan"):
            with st.spinner("Generando nuevo plan..."):
                new_plan, message = generate_learning_plan(username)
            if new_plan:
                save_learning_plan(username, new_plan)
                st.success("Plan actualizado exitosamente")
                st.rerun()
            else:
                st.error(message)

    if st.button("⬅️ Volver al dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()