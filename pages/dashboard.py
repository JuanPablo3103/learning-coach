import streamlit as st

def show():
    # Verificar que está logueado
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    st.title("🎓 Personal Learning Coach")
    st.markdown("---")

    # Mensaje de bienvenida
    name = st.session_state.get("name", "")
    st.header(f"Bienvenido, {name}! 👋")
    st.subheader("¿Qué quieres aprender hoy?")

    st.markdown("---")

    # Tarjetas de módulos
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

    # Botón cerrar sesión
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()