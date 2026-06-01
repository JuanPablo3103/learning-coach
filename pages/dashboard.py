import streamlit as st
from utils.agent import (
    load_learning_plan, get_quiz_results, get_task_progress,
    check_progress_alerts, get_decision_history, log_decision, AI_AVAILABLE
)


def show():
    """Página del tablero (dashboard) con estadísticas, alertas y historial."""
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")

    st.markdown("""
    <style>
        .block-container { max-width: 700px !important; padding-top: 2rem !important; }
        .dash-header { font-size: 24px; font-weight: 600; color: #E8E6F0; margin-bottom: 0.2rem; }
        .dash-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 1.5rem; }
        .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.5rem; }
        .stat-card {
            background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.08);
            border-radius: 12px; padding: 1.2rem; text-align: center;
        }
        .stat-value { font-size: 28px; font-weight: 700; color: #A9A3E8; }
        .stat-label { font-size: 11px; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
        .alert-card {
            border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.8rem;
            border-left: 4px solid;
        }
        .alert-behind { background: rgba(239,68,68,0.08); border-color: #F87171; }
        .alert-ahead { background: rgba(74,222,128,0.08); border-color: #4ADE80; }
        .alert-on_track { background: rgba(251,191,36,0.08); border-color: #FBBF24; }
        .alert-msg { font-size: 14px; color: #E8E6F0; margin-bottom: 4px; }
        .alert-action { font-size: 13px; color: rgba(255,255,255,0.45); }
        .history-item {
            padding: 0.7rem 1rem; border-bottom: 0.5px solid rgba(255,255,255,0.06);
            display: flex; justify-content: space-between; align-items: center;
        }
        .history-text { font-size: 13px; color: #E8E6F0; }
        .history-type {
            font-size: 10px; padding: 2px 8px; border-radius: 4px;
            background: rgba(83,74,183,0.2); color: #A9A3E8; text-transform: uppercase;
        }
        .history-date { font-size: 11px; color: rgba(255,255,255,0.25); margin-top: 2px; }
        .mode-badge {
            display: inline-block; font-size: 11px; padding: 3px 10px; border-radius: 6px;
            margin-bottom: 1rem;
        }
        .mode-local { background: rgba(251,191,36,0.15); color: #FBBF24; }
        .mode-ai { background: rgba(74,222,128,0.15); color: #4ADE80; }
    </style>
    """, unsafe_allow_html=True)

    name = st.session_state.get("name", username)
    st.markdown(f'<div class="dash-header">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dash-sub">¡Hola, {name}! Aquí está tu resumen de progreso</div>', unsafe_allow_html=True)

    # Mode badge
    if AI_AVAILABLE:
        st.markdown('<span class="mode-badge mode-ai">🤖 Modo IA activo</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="mode-badge mode-local">⚡ Modo local (fallback)</span>', unsafe_allow_html=True)

    # ── Stats ──
    plan = load_learning_plan(username)
    progress = get_task_progress(username)
    quizzes = get_quiz_results(username)

    total_tasks = 0
    completed_tasks = 0
    if plan:
        for week in plan.get("weeks", []):
            for day in week.get("days", []):
                total_tasks += 1
                if progress.get(f"{week['week']}-{day['day']}"):
                    completed_tasks += 1

    avg_score = 0
    if quizzes:
        avg_score = sum(q["score"] / q["total"] * 100 for q in quizzes if q["total"]) / len(quizzes)

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-value">{completed_tasks}/{total_tasks}</div>
            <div class="stat-label">Tareas completadas</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(quizzes)}</div>
            <div class="stat-label">Quizzes realizados</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{avg_score:.0f}%</div>
            <div class="stat-label">Promedio quizzes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Progress bar ──
    if total_tasks > 0:
        pct = completed_tasks / total_tasks
        st.progress(pct, text=f"Progreso general: {pct:.0%}")

    # ── Alerts ──
    st.markdown("### 🔔 Alertas de Progreso")
    alerts = check_progress_alerts(username)
    if alerts:
        for a in alerts:
            atype = a.get("type", "on_track")
            st.markdown(f"""
            <div class="alert-card alert-{atype}">
                <div class="alert-msg">{a['icon']} {a['message']}</div>
                <div class="alert-action">💡 {a['action']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Log alert
            log_decision(username, f"alert_{atype}", a["message"], a["action"])
    else:
        st.info("No hay alertas por ahora. ¡Genera un plan y completa tareas!")

    # ── Decision History ──
    st.markdown("### 📜 Historial de Decisiones")
    history = get_decision_history(username)
    if history:
        for h in history[:15]:
            st.markdown(f"""
            <div class="history-item">
                <div>
                    <div class="history-text">{h['message']}</div>
                    <div class="history-date">{h.get('created_at', '')}</div>
                </div>
                <span class="history-type">{h['event_type']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sin eventos registrados aún.")
