import streamlit as st
from utils.agent import load_learning_plan, save_learning_plan, negotiate_plan

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")
    plan = load_learning_plan(username)

    st.markdown("""
    <style>
        .block-container { max-width: 640px !important; padding-top: 2.5rem !important; }
        .stApp { background: #0F0E1A !important; }
        .ng-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 2rem; }
        .ng-logo-icon { width: 40px; height: 40px; border-radius: 10px; background: #534AB7; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .ng-logo-text { font-size: 16px; font-weight: 500; color: #E8E6F0; }
        .ng-logo-sub { font-size: 12px; color: rgba(255,255,255,0.35); }
        .ng-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .ng-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 1.75rem; }
        .ng-current { background: rgba(83,74,183,0.12); border: 0.5px solid rgba(83,74,183,0.25); border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 1.5rem; font-size: 13px; color: #A9A3E8; }
        .ng-examples { background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.07); border-radius: 10px; padding: 1rem 1.1rem; margin-bottom: 1.25rem; }
        .ng-examples-title { font-size: 12px; color: rgba(255,255,255,0.45); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.6rem; }
        .ng-example { font-size: 13px; color: rgba(255,255,255,0.55); margin-bottom: 0.35rem; }
        .stButton > button {
            width: 100% !important; background: rgba(255,255,255,0.04) !important;
            border: 0.5px solid rgba(255,255,255,0.1) !important;
            border-radius: 10px !important; color: #E8E6F0 !important;
            font-size: 14px !important; font-weight: 500 !important; padding: 0.7rem 1rem !important;
        }
        .stButton > button:hover {
            border-color: #534AB7 !important; background: rgba(83,74,183,0.15) !important; color: #FFFFFF !important;
        }
    </style>

    <div class="ng-logo">
        <div class="ng-logo-icon">🧠</div>
        <div>
            <div class="ng-logo-text">Learning Coach</div>
            <div class="ng-logo-sub">Tu coach de aprendizaje con IA</div>
        </div>
    </div>
    <div class="ng-title">🤝 Negociar mi plan</div>
    <div class="ng-sub">Dile al agente qué quieres ajustar y él adaptará tu plan actual</div>
    """, unsafe_allow_html=True)

    if not plan:
        st.warning("Aún no tienes un plan. Genera uno primero para poder negociar cambios.")
        if st.button("📅 Ir a Mi Plan"):
            st.session_state.page = "plan"
            st.rerun()
        if st.button("⬅️ Volver al dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return

    # Resumen del plan actual
    st.markdown(f'<div class="ng-current">📋 Plan actual: <b>{plan["topic"]}</b> · {plan["duration_weeks"]} semanas · {plan["weekly_hours"]} horas/día</div>', unsafe_allow_html=True)

    # Ejemplos de peticiones
    st.markdown(
        '<div class="ng-examples">'
        '<div class="ng-examples-title">Ejemplos de lo que puedes pedir</div>'
        '<div class="ng-example">• Tengo menos tiempo, redúcelo a 30 minutos por día</div>'
        '<div class="ng-example">• Ya domino lo básico, sáltate la introducción</div>'
        '<div class="ng-example">• Quiero más ejercicios prácticos y menos teoría</div>'
        '<div class="ng-example">• Cambia los videos por artículos para leer</div>'
        '</div>',
        unsafe_allow_html=True
    )

    feedback = st.text_area(
        "¿Qué quieres cambiar de tu plan?",
        placeholder="Ej: Esta semana tengo poco tiempo, reduce la carga de trabajo...",
        height=120
    )

    if st.button("🤝 Negociar con el agente", use_container_width=True):
        if feedback.strip():
            with st.spinner("El agente está ajustando tu plan..."):
                new_plan, message = negotiate_plan(username, feedback)
            if new_plan:
                st.session_state.proposed_plan = new_plan
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Escribe primero qué quieres cambiar.")

    # Propuesta del agente (preview + aceptar/descartar)
    if st.session_state.get("proposed_plan"):
        proposed = st.session_state.proposed_plan
        st.markdown("---")
        st.markdown("### 📋 Propuesta del agente")
        st.caption("Revisa los cambios antes de aceptarlos.")

        for week in proposed["weeks"]:
            with st.expander(f"Semana {week['week']} — {week['title']}", expanded=False):
                st.markdown(f"*{week['objective']}*")
                for day in week["days"]:
                    st.markdown(f"**{day['day']}** · {day['topic']}")
                    for res in day.get("resources", []):
                        st.markdown(f"&nbsp;&nbsp;&nbsp;🔗 {res['title']} · {res.get('duration_minutes', '?')} min")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Aceptar cambios", use_container_width=True):
                save_learning_plan(username, proposed)
                st.session_state.proposed_plan = None
                st.success("¡Plan actualizado con los cambios!")
                st.rerun()
        with col2:
            if st.button("❌ Descartar", use_container_width=True):
                st.session_state.proposed_plan = None
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Volver al dashboard"):
        st.session_state.proposed_plan = None
        st.session_state.page = "dashboard"
        st.rerun()