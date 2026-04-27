import streamlit as st
from utils.profile import get_profile, profile_exists

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
        st.success(f"📚 Tema actual: **{profile['topic']}**")
        st.subheader("¿Qué quieres hacer hoy?")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.info("📅 Mi Plan de Aprendizaje")
            st.button("Ver mi plan", key="plan")
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