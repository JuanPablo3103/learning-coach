import streamlit as st
from utils.profile import get_profile, save_profile

KNOWLEDGE_LEVELS = [
    "Principiante — No sé nada del tema",
    "Básico — Conozco algunos conceptos",
    "Intermedio — Tengo experiencia práctica",
    "Avanzado — Domino el tema"
]

TOPICS = [
    "Cloud Computing",
    "DevOps",
    "Data Science",
    "Machine Learning",
    "Desarrollo Web",
    "Desarrollo Mobile",
    "Ciberseguridad",
    "Inteligencia Artificial",
    "Blockchain",
    "Otro"
]

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")
    existing_profile = get_profile(username)

    if existing_profile:
        st.title("✏️ Editar perfil de aprendizaje")
    else:
        st.title("👤 Crear perfil de aprendizaje")

    st.subheader("Cuéntanos sobre ti para personalizar tu plan")
    st.markdown("---")

    # Valores por defecto si ya tiene perfil
    default_topic = existing_profile.get("topic", TOPICS[0]) if existing_profile else TOPICS[0]
    default_hours = existing_profile.get("available_hours", 1) if existing_profile else 1
    default_knowledge = existing_profile.get("prior_knowledge", KNOWLEDGE_LEVELS[0]) if existing_profile else KNOWLEDGE_LEVELS[0]
    default_goals = existing_profile.get("goals", "") if existing_profile else ""

    with st.form("profile_form"):
        topic = st.selectbox(
            "📚 ¿Qué tema quieres aprender?",
            TOPICS,
            index=TOPICS.index(default_topic) if default_topic in TOPICS else 0
        )

        available_hours = st.slider(
            "⏰ ¿Cuántas horas por día puedes estudiar?",
            min_value=1,
            max_value=8,
            value=default_hours
        )

        prior_knowledge = st.selectbox(
            "🧠 ¿Cuál es tu nivel de conocimiento previo?",
            KNOWLEDGE_LEVELS,
            index=KNOWLEDGE_LEVELS.index(default_knowledge) if default_knowledge in KNOWLEDGE_LEVELS else 0
        )

        goals = st.text_area(
            "🎯 ¿Cuál es tu objetivo principal?",
            value=default_goals,
            placeholder="Ej: Quiero conseguir trabajo como desarrollador web en 3 meses"
        )

        submit = st.form_submit_button("💾 Guardar perfil")

    if submit:
        if not goals:
            st.error("❌ Por favor describe tu objetivo principal")
        else:
            success, message = save_profile(
                username, topic, available_hours,
                prior_knowledge, goals
            )
            if success:
                st.success(f"✅ {message}")
                st.balloons()

    st.markdown("---")
    if st.button("⬅️ Volver al dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()