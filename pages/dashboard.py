import streamlit as st
from utils.profile import get_profile, profile_exists
from utils.agent import load_learning_plan

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    st.title("🎓 Personal Learning Coach")
    st.markdown("---")

    name = st.session_state.get("name", "")
    username = st.session_state.get("username", "")
    st.header(f"Bienvenido, {name}! 👋")

    # Verificar si tiene perfil
    if not profile_exists(username):
        st.warning("⚠️ Aún no tienes un perfil de aprendizaje.")
        st.info("Crea tu perfil para que el coach pueda personalizar tu plan.")
        if st.button("👤 Crear mi perfil"):
            st.session_state.page = "profile"
            st.rerun()
    else:
        profile = get_profile(username)
        plan = load_learning_plan(username)

        st.success(f"📚 Tema actual: **{profile['topic']}**")

        if plan:
            st.info(f"📅 Tienes un plan de **{plan['duration_weeks']} semanas** activo")
        else:
            st.warning("⚠️ Aún no tienes un plan de aprendizaje generado")

        st.subheader("¿Qué quieres hacer hoy?")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.info("📅 Mi Plan de Aprendizaje")
            if st.button("Ver mi plan", key="plan"):
                st.session_state.page = "plan"
                st.rerun()
        with col2:
            st.info("📊 Mi Progreso")
            st.button("Ver progreso", key="progress")

        col3, col4 = st.columns(2)
        with col3:
            st.info("📝 Quizzes")
            st.button("Hacer quiz", key="quiz")
        with col4:
            st.info("🔍 Recursos")
            st.button("Ver recursos", key="resources")

        st.markdown("---")

        if st.button("✏️ Editar mi perfil"):
            st.session_state.page = "profile"
            st.rerun()

    st.markdown("---")

    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()