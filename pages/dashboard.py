import streamlit as st
from utils.profile import get_profile, profile_exists
from utils.agent import load_learning_plan

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    name = st.session_state.get("name", "")
    username = st.session_state.get("username", "")

    st.markdown("""
    <style>
        .block-container { max-width: 720px !important; padding-top: 0.5rem !important; }
        .stApp { background: #0F0E1A !important; }
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .logo-icon {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: #534AB7;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        .logo-text {
            font-size: 15px;
            font-weight: 500;
            color: #E8E6F0;
        }
        .welcome-title {
            font-size: 24px;
            font-weight: 500;
            color: #E8E6F0;
            margin-bottom: 0.3rem;
        }
        .welcome-sub {
            font-size: 14px;
            color: rgba(255,255,255,0.4);
            margin-bottom: 1.5rem;
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 2rem;
        }
        .status-card-topic {
            background: rgba(83,74,183,0.15);
            border: 0.5px solid rgba(83,74,183,0.3);
            border-radius: 12px;
            padding: 1rem 1.25rem;
        }
        .status-card-plan {
            background: rgba(29,158,117,0.12);
            border: 0.5px solid rgba(29,158,117,0.25);
            border-radius: 12px;
            padding: 1rem 1.25rem;
        }
        .card-label {
            font-size: 11px;
            color: rgba(255,255,255,0.4);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .card-value {
            font-size: 15px;
            font-weight: 500;
            color: #E8E6F0;
        }
        .card-icon-purple { font-size: 18px; color: #7F77DD; margin-bottom: 8px; }
        .card-icon-teal { font-size: 18px; color: #1D9E75; margin-bottom: 8px; }
        .section-title {
            font-size: 12px;
            color: rgba(255,255,255,0.35);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 1rem;
        }
        .nav-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 2rem;
        }
        .nav-card {
            background: rgba(255,255,255,0.04);
            border: 0.5px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        .nav-icon-purple {
            width: 36px; height: 36px;
            border-radius: 8px;
            background: rgba(83,74,183,0.2);
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; color: #7F77DD; flex-shrink: 0;
        }
        .nav-icon-teal {
            width: 36px; height: 36px;
            border-radius: 8px;
            background: rgba(29,158,117,0.15);
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; color: #1D9E75; flex-shrink: 0;
        }
        .nav-icon-amber {
            width: 36px; height: 36px;
            border-radius: 8px;
            background: rgba(186,117,23,0.15);
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; color: #BA7517; flex-shrink: 0;
        }
        .nav-icon-coral {
            width: 36px; height: 36px;
            border-radius: 8px;
            background: rgba(216,90,48,0.15);
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; color: #D85A30; flex-shrink: 0;
        }
        .nav-card-title {
            font-size: 14px;
            font-weight: 500;
            color: #E8E6F0;
            margin-bottom: 3px;
        }
        .nav-card-sub {
            font-size: 12px;
            color: rgba(255,255,255,0.35);
        }
        .stButton > button {
            background: transparent !important;
            border: 0.5px solid rgba(255,255,255,0.12) !important;
            border-radius: 8px !important;
            color: rgba(255,255,255,0.45) !important;
            font-size: 13px !important;
        }
        .stButton > button:hover {
            border-color: #534AB7 !important;
            color: #7F77DD !important;
        }
    </style>

    <div class="topbar">
        <div class="logo">
            <div class="logo-icon">🧠</div>
            <span class="logo-text">Learning Coach</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    profile = get_profile(username)
    plan = load_learning_plan(username)

    if not profile_exists(username):
        st.markdown(f'<div class="welcome-title">Hola, {name} 👋</div>', unsafe_allow_html=True)
        st.markdown('<div class="welcome-sub">Crea tu perfil para comenzar tu camino de aprendizaje</div>', unsafe_allow_html=True)
        st.warning("Aún no tienes un perfil de aprendizaje.")
        if st.button("👤 Crear mi perfil"):
            st.session_state.page = "profile"
            st.rerun()
    else:
        st.markdown(f'<div class="welcome-title">Hola, {name} 👋</div>', unsafe_allow_html=True)
        st.markdown('<div class="welcome-sub">Aquí tienes un resumen de tu progreso de hoy</div>', unsafe_allow_html=True)

        plan_text = f"{plan['duration_weeks']} semanas activo" if plan else "Sin plan generado"
        plan_icon = "📅" if plan else "⚠️"

        st.markdown(f"""
        <div class="status-grid">
            <div class="status-card-topic">
                <div class="card-icon-purple">📚</div>
                <div class="card-label">Tema actual</div>
                <div class="card-value">{profile['topic']}</div>
            </div>
            <div class="status-card-plan">
                <div class="card-icon-teal">{plan_icon}</div>
                <div class="card-label">Plan activo</div>
                <div class="card-value">{plan_text}</div>
            </div>
        </div>

        <div class="section-title">¿Qué quieres hacer hoy?</div>

        <div class="nav-grid">
            <div class="nav-card">
                <div class="nav-icon-purple">📅</div>
                <div>
                    <div class="nav-card-title">Mi plan de aprendizaje</div>
                    <div class="nav-card-sub">Ver tu plan día a día con recursos</div>
                </div>
            </div>
            <div class="nav-card">
                <div class="nav-icon-teal">🗺️</div>
                <div>
                    <div class="nav-card-title">Mi hoja de ruta</div>
                    <div class="nav-card-sub">Vista general de tu camino</div>
                </div>
            </div>
            <div class="nav-card">
                <div class="nav-icon-amber">❓</div>
                <div>
                    <div class="nav-card-title">Quizzes</div>
                    <div class="nav-card-sub">Pon a prueba tu conocimiento</div>
                </div>
            </div>
            <div class="nav-card">
                <div class="nav-icon-coral">🔍</div>
                <div>
                    <div class="nav-card-title">Recursos externos</div>
                    <div class="nav-card-sub">Buscar materiales de estudio</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 Ver mi plan", use_container_width=True):
                st.session_state.page = "plan"
                st.rerun()
        with col2:
            if st.button("🗺️ Ver hoja de ruta", use_container_width=True):
                st.session_state.page = "roadmap"
                st.rerun()

        col3, col4 = st.columns(2)
        with col3:
            if st.button("❓ Hacer quiz", use_container_width=True):
                pass
        with col4:
            if st.button("🔍 Ver recursos", use_container_width=True):
                pass

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Editar mi perfil"):
            st.session_state.page = "profile"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()