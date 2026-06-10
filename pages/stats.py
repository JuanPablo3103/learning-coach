import streamlit as st
import pandas as pd
from utils.agent import load_learning_plan, get_learning_stats

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
        .st-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .st-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .st-section { font-size: 13px; color: rgba(255,255,255,0.5); font-weight: 500; margin: 1.5rem 0 0.5rem 0; }
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

    <div class="st-title">📊 Tus Estadísticas</div>
    <div class="st-sub">Tu progreso de aprendizaje en números</div>
    """, unsafe_allow_html=True)

    if not plan:
        st.warning("Aún no tienes un plan generado. Genera uno para ver tus estadísticas.")
        if st.button("📅 Ir a Mi Plan"):
            st.session_state.page = "plan"
            st.rerun()
        if st.button("⬅️ Volver al dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return

    stats = get_learning_stats(username)

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Tareas totales", stats["total"])
    col2.metric("Completadas", stats["completed"])
    col3.metric("Progreso", f"{stats['pct']}%")

    # Barra de progreso general
    st.progress(stats["pct"] / 100)

    if stats["completed"] == 0:
        st.info("Aún no has completado ninguna tarea. ¡Empieza marcando recursos en tu hoja de ruta!")
    elif stats["pct"] >= 80:
        st.success(f"¡Excelente! Vas al {stats['pct']}% de tu plan. 🚀")

    # Avance por semana
    st.markdown('<div class="st-section">Avance por semana</div>', unsafe_allow_html=True)

    if stats["per_week"]:
        rows = []
        for w in sorted(stats["per_week"].keys()):
            d = stats["per_week"][w]
            rows.append({
                "Semana": f"Semana {w}",
                "Completadas": d["completed"],
                "Pendientes": d["total"] - d["completed"],
            })
        df = pd.DataFrame(rows).set_index("Semana")
        st.bar_chart(df, color=["#7F77DD", "#3A3658"])

    if st.button("⬅️ Volver al dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()