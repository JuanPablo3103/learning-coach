import streamlit as st
from utils.profile import get_profile, profile_exists
from utils.agent import load_learning_plan, get_learning_stats, check_progress_alerts

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    name = st.session_state.get("name", "")
    username = st.session_state.get("username", "")

    st.markdown("""
    <style>
        .block-container { max-width: 720px !important; padding-top: 1.5rem !important; }
        .stApp { background: #0F0E1A !important; }
        .topbar { display: flex; align-items: center; margin-bottom: 2.5rem; }
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo-icon { width: 36px; height: 36px; border-radius: 8px; background: #534AB7; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .logo-text { font-size: 15px; font-weight: 500; color: #E8E6F0; }
        .welcome-title { font-size: 26px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.4rem; }
        .welcome-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 1.5rem; }
        .status-card-topic { background: rgba(83,74,183,0.15); border: 0.5px solid rgba(83,74,183,0.3); border-radius: 14px; padding: 1.1rem 1.35rem; }
        .status-card-plan { background: rgba(29,158,117,0.12); border: 0.5px solid rgba(29,158,117,0.25); border-radius: 14px; padding: 1.1rem 1.35rem; }
        .card-label { font-size: 11px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
        .card-value { font-size: 15px; font-weight: 500; color: #E8E6F0; }
        .card-icon-purple { font-size: 18px; color: #7F77DD; margin-bottom: 8px; }
        .card-icon-teal { font-size: 18px; color: #1D9E75; margin-bottom: 8px; }
        .progress-card { background: rgba(255,255,255,0.04); border: 0.5px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 1.25rem 1.35rem; margin-bottom: 1.5rem; }
        .progress-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .progress-label { font-size: 13px; color: #E8E6F0; font-weight: 500; }
        .progress-pct { font-size: 16px; color: #7F77DD; font-weight: 700; }
        .progress-track { width: 100%; height: 8px; background: rgba(255,255,255,0.08); border-radius: 99px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #534AB7, #7F77DD); border-radius: 99px; }
        .progress-detail { font-size: 12px; color: rgba(255,255,255,0.4); margin-top: 10px; }
        .alert-section { margin-bottom: 2.5rem; }
        .alert-box { display: flex; align-items: flex-start; gap: 10px; border-radius: 12px; padding: 0.85rem 1.1rem; margin-bottom: 10px; font-size: 13px; line-height: 1.4; }
        .alert-warning { background: rgba(221,170,127,0.10); border: 0.5px solid rgba(221,170,127,0.30); color: #E8D2B8; }
        .alert-success { background: rgba(29,158,117,0.10); border: 0.5px solid rgba(29,158,117,0.28); color: #A8E6CE; }
        .alert-icon { font-size: 15px; flex-shrink: 0; }
        .section-title { font-size: 12px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 1rem; }
        .divider { height: 0.5px; background: rgba(255,255,255,0.08); margin: 2rem 0 1.5rem 0; }
        .stButton > button {
            width: 100% !important;
            background: rgba(255,255,255,0.04) !important;
            border: 0.5px solid rgba(255,255,255,0.09) !important;
            border-radius: 12px !important;
            color: #E8E6F0 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 0.85rem 1rem !important;
            transition: all 0.15s ease !important;
        }
        .stButton > button:hover {
            border-color: #534AB7 !important;
            background: rgba(83,74,183,0.15) !important;
            color: #FFFFFF !important;
        }
        div[data-testid="column"] { gap: 14px !important; }
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

        # Tarjetas de estado
        st.markdown(f'<div class="status-grid"><div class="status-card-topic"><div class="card-icon-purple">📚</div><div class="card-label">Tema actual</div><div class="card-value">{profile["topic"]}</div></div><div class="status-card-plan"><div class="card-icon-teal">{plan_icon}</div><div class="card-label">Plan activo</div><div class="card-value">{plan_text}</div></div></div>', unsafe_allow_html=True)

        # Tarjeta de progreso
        if plan:
            stats = get_learning_stats(username)
            st.markdown(f'<div class="progress-card"><div class="progress-head"><span class="progress-label">📈 Tu progreso</span><span class="progress-pct">{stats["pct"]}%</span></div><div class="progress-track"><div class="progress-fill" style="width:{stats["pct"]}%;"></div></div><div class="progress-detail">{stats["completed"]} de {stats["total"]} tareas completadas</div></div>', unsafe_allow_html=True)

            # Alertas de progreso del agente
            alerts = check_progress_alerts(username)
            if alerts:
                alerts_html = '<div class="alert-section">'
                for a in alerts:
                    cls = "alert-success" if a["type"] == "success" else "alert-warning"
                    icon = "🎉" if a["type"] == "success" else "⚠️"
                    alerts_html += f'<div class="alert-box {cls}"><span class="alert-icon">{icon}</span><span>{a["message"]}</span></div>'
                alerts_html += '</div>'
                st.markdown(alerts_html, unsafe_allow_html=True)

        # ─── Acciones principales ───
        st.markdown('<div class="section-title">¿Qué quieres hacer hoy?</div>', unsafe_allow_html=True)

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
            if st.button("🤝 Negociar mi plan", use_container_width=True):
                st.session_state.page = "negotiate"
                st.rerun()
        with col4:
            if st.button("📊 Ver estadísticas", use_container_width=True):
                st.session_state.page = "stats"
                st.rerun()

        col5, col6 = st.columns(2)
        with col5:
            if st.button("❓ Hacer quiz", use_container_width=True):
                st.session_state.page = "quiz"
                st.rerun()
        with col6:
            if st.button("🔍 Ver recursos", use_container_width=True):
                st.toast("🚧 Disponible próximamente (Sprint 4)")

        # ─── Acciones secundarias ───
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        col7, col8 = st.columns(2)
        with col7:
            if st.button("✏️ Editar mi perfil", use_container_width=True):
                st.session_state.page = "profile"
                st.rerun()
        with col8:
            if st.button("🚪 Cerrar sesión", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        return

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()