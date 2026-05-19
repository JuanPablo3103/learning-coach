import streamlit as st
from utils.profile import get_profile, save_profile

TOPICS = [
    "☁️ Cloud Computing",
    "⚙️ DevOps",
    "📊 Data Science",
    "🤖 Machine Learning",
    "🌐 Desarrollo Web",
    "📱 Desarrollo Mobile",
    "🔐 Ciberseguridad",
    "🧠 Inteligencia Artificial",
    "🔗 Blockchain",
]

LEVELS = [
    "🌱 Principiante — No sé nada del tema",
    "📖 Básico — Conozco algunos conceptos",
    "⚡ Intermedio — Tengo experiencia práctica",
    "🏆 Avanzado — Domino el tema",
]

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")
    existing_profile = get_profile(username)
    is_edit = existing_profile is not None

    default_topic = existing_profile.get("topic", TOPICS[0]) if existing_profile else TOPICS[0]
    default_hours = int(existing_profile.get("available_hours", 2)) if existing_profile else 2
    default_knowledge = existing_profile.get("prior_knowledge", LEVELS[0]) if existing_profile else LEVELS[0]
    default_goals = existing_profile.get("goals", "") if existing_profile else ""

    # Buscar índice correcto
    topic_match = next((t for t in TOPICS if existing_profile and existing_profile.get("topic", "") in t), TOPICS[0]) if existing_profile else TOPICS[0]
    level_match = next((l for l in LEVELS if existing_profile and existing_profile.get("prior_knowledge", "") in l), LEVELS[0]) if existing_profile else LEVELS[0]

    st.markdown("""
    <style>
        .block-container { max-width: 560px !important; padding-top: 2.5rem !important; }
        .stApp { background: #0F0E1A !important; }
        .pro-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 2rem; }
        .pro-logo-icon { width: 40px; height: 40px; border-radius: 10px; background: #534AB7; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .pro-logo-text { font-size: 16px; font-weight: 500; color: #E8E6F0; }
        .pro-logo-sub { font-size: 12px; color: rgba(255,255,255,0.35); }
        .pro-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .pro-subtitle { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .pro-section-title {
            font-size: 11px; color: rgba(255,255,255,0.35);
            text-transform: uppercase; letter-spacing: 0.6px;
            margin-bottom: 0.5rem; margin-top: 1.25rem;
        }
        /* Radio como tarjetas */
        div[data-testid="stRadio"] > div {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 8px !important;
        }
        div[data-testid="stRadio"] > div > label {
            background: rgba(255,255,255,0.03) !important;
            border: 0.5px solid rgba(255,255,255,0.08) !important;
            border-radius: 8px !important;
            padding: 10px 8px !important;
            color: rgba(255,255,255,0.5) !important;
            font-size: 12px !important;
            text-align: center !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        div[data-testid="stRadio"] > div > label:has(input:checked) {
            background: rgba(83,74,183,0.25) !important;
            border: 1.5px solid #534AB7 !important;
            color: #EEEDFE !important;
            font-weight: 600 !important;
        }
        div[data-testid="stRadio"] > div > label > div:first-child {
            display: none !important;
        }
        div[data-testid="stRadio"] > label {
            display: none !important;
        }
        /* Niveles en 2 columnas */
        div[data-testid="stRadio"].levels-radio > div {
            grid-template-columns: repeat(2, 1fr) !important;
        }
        div[data-testid="stForm"] {
            background: transparent !important; border: none !important; padding: 0 !important;
        }
        .stSlider > label { display: none !important; }
        .stTextArea > label { display: none !important; }
        .stFormSubmitButton > button {
            width: 100% !important; background: #534AB7 !important;
            color: #EEEDFE !important; border: none !important;
            border-radius: 8px !important; padding: 11px !important;
            font-size: 14px !important; font-weight: 500 !important;
            margin-top: 0.5rem !important;
        }
        .stFormSubmitButton > button:hover { background: #3C3489 !important; }
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
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="pro-logo">
        <div class="pro-logo-icon">🧠</div>
        <div>
            <div class="pro-logo-text">Learning Coach</div>
            <div class="pro-logo-sub">Tu coach de aprendizaje con IA</div>
        </div>
    </div>
    <div class="pro-title">{"✏️ Editar perfil" if is_edit else "👤 Crear perfil de aprendizaje"}</div>
    <div class="pro-subtitle">Cuéntanos sobre ti para personalizar tu plan.</div>
    <div class="pro-section-title">¿Qué tema quieres aprender?</div>
    """, unsafe_allow_html=True)

    topic = st.radio(
        "Tema",
        TOPICS,
        index=TOPICS.index(topic_match) if topic_match in TOPICS else 0,
        horizontal=False,
        key="radio_topic"
    )

    st.markdown('<div class="pro-section-title">¿Cuál es tu nivel de conocimiento previo?</div>', unsafe_allow_html=True)

    level = st.radio(
        "Nivel",
        LEVELS,
        index=LEVELS.index(level_match) if level_match in LEVELS else 0,
        horizontal=False,
        key="radio_level"
    )

    with st.form("profile_form"):
        st.markdown('<div class="pro-section-title">¿Cuántas horas por día puedes estudiar?</div>', unsafe_allow_html=True)
        available_hours = st.slider("", min_value=1, max_value=8, value=default_hours, step=1)

        st.markdown('<div class="pro-section-title">¿Cuál es tu objetivo principal?</div>', unsafe_allow_html=True)
        goals = st.text_area("", value=default_goals,
            placeholder="Ej: Quiero conseguir trabajo como desarrollador web en 3 meses",
            height=100)

        submit = st.form_submit_button("💾 Guardar perfil")

    if submit:
        if not goals:
            st.error("Por favor describe tu objetivo principal")
        else:
            topic_clean = topic.split(" ", 1)[1] if " " in topic else topic
            success, message = save_profile(
                username, topic_clean, available_hours, level, goals
            )
            if success:
                st.success(message)
                st.balloons()

    if st.button("⬅️ Volver al dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()