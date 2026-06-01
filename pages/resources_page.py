import streamlit as st
from utils.resources import search_resources
from utils.agent import load_learning_plan


def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")

    st.markdown("""
    <style>
        .block-container { max-width: 680px !important; padding-top: 2rem !important; }
        .res-header { font-size: 22px; font-weight: 600; color: #E8E6F0; margin-bottom: 0.3rem; }
        .res-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 1.5rem; }
        .res-card {
            background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.08);
            border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.8rem;
            transition: border-color 0.2s;
        }
        .res-card:hover { border-color: rgba(83,74,183,0.5); }
        .res-type-badge {
            display: inline-block; font-size: 10px; text-transform: uppercase;
            letter-spacing: 0.8px; padding: 2px 8px; border-radius: 4px;
            margin-bottom: 6px; font-weight: 600;
        }
        .badge-video { background: rgba(239,68,68,0.15); color: #F87171; }
        .badge-article { background: rgba(59,130,246,0.15); color: #60A5FA; }
        .badge-course { background: rgba(16,185,129,0.15); color: #34D399; }
        .res-title { font-size: 15px; font-weight: 500; color: #E8E6F0; margin-bottom: 4px; }
        .res-title a { color: #7F77DD; text-decoration: none; }
        .res-title a:hover { text-decoration: underline; }
        .res-snippet { font-size: 13px; color: rgba(255,255,255,0.4); line-height: 1.4; }
    </style>
    <div class="res-header">🔍 Recursos Externos</div>
    <div class="res-sub">Recursos educativos buscados automáticamente para tu plan</div>
    """, unsafe_allow_html=True)

    plan = load_learning_plan(username)

    # ── Manual search ──
    st.markdown("#### Buscar recursos por tema")
    custom_query = st.text_input("Tema a buscar:", placeholder="Ej: Python asyncio, Machine Learning basics...")
    if st.button("🔎 Buscar", use_container_width=True) and custom_query:
        with st.spinner("Buscando recursos..."):
            results = search_resources(custom_query)
        _render_resources(results)

    # ── Plan-based resources ──
    if plan:
        st.markdown("---")
        st.markdown("#### 📚 Recursos por tema del plan")

        topics = []
        for week in plan.get("weeks", []):
            for day in week.get("days", []):
                topics.append((f"Sem {week['week']} · {day['day']}", day["topic"]))

        if topics:
            selected = st.selectbox("Selecciona un tema:", [f"{t[0]} — {t[1]}" for t in topics])
            idx = [f"{t[0]} — {t[1]}" for t in topics].index(selected)
            topic_name = topics[idx][1]

            if st.button("📖 Buscar recursos para este tema", use_container_width=True):
                with st.spinner(f"Buscando recursos para '{topic_name}'..."):
                    results = search_resources(topic_name)
                _render_resources(results)
    else:
        st.info("💡 Genera un plan de aprendizaje para ver recursos por tema.")


def _render_resources(resources):
    """Renderiza las tarjetas de recursos."""
    if not resources:
        st.warning("No se encontraron recursos.")
        return

    icons = {"video": "🎬", "article": "📖", "course": "🎓"}
    badge_classes = {"video": "badge-video", "article": "badge-article", "course": "badge-course"}

    for r in resources:
        rtype = r.get("type", "article")
        badge_cls = badge_classes.get(rtype, "badge-article")
        icon = icons.get(rtype, "🔗")
        st.markdown(f"""
        <div class="res-card">
            <span class="res-type-badge {badge_cls}">{icon} {rtype}</span>
            <div class="res-title"><a href="{r['url']}" target="_blank">{r['title']}</a></div>
            <div class="res-snippet">{r.get('snippet', '')}</div>
        </div>
        """, unsafe_allow_html=True)
