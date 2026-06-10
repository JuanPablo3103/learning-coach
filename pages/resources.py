import streamlit as st
from utils.profile import get_profile, profile_exists
from utils.resources import search_resources, index_topic_resources, get_topic_resources


def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")

    st.markdown("""
    <style>
        .block-container { max-width: 640px !important; padding-top: 2.5rem !important; }
        .stApp { background: #0F0E1A !important; }
        .rs-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .rs-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .rs-section { font-size: 13px; color: rgba(255,255,255,0.5); font-weight: 500; margin: 1.5rem 0 0.5rem 0; }
        .rs-card { background: rgba(255,255,255,0.02); border: 0.5px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.9rem; }
        .rs-head { display: flex; align-items: center; gap: 8px; margin-bottom: 0.4rem; }
        .rs-icon { font-size: 16px; }
        .rs-rtitle { font-size: 15px; font-weight: 500; color: #E8E6F0; flex: 1; }
        .rs-relevance { font-size: 11px; color: #A9A3E8; background: rgba(83,74,183,0.18); border: 0.5px solid rgba(83,74,183,0.3); border-radius: 6px; padding: 2px 8px; flex-shrink: 0; }
        .rs-desc { font-size: 13px; color: rgba(255,255,255,0.5); margin-bottom: 0.6rem; line-height: 1.4; }
        .rs-meta { display: flex; gap: 8px; align-items: center; margin-bottom: 0.6rem; }
        .rs-tag { font-size: 11px; color: rgba(255,255,255,0.4); background: rgba(255,255,255,0.04); border-radius: 5px; padding: 2px 8px; }
        .rs-link { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: #7F77DD; text-decoration: none; }
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
    <div class="rs-title">🔍 Recursos de Aprendizaje</div>
    <div class="rs-sub">Búsqueda semántica de recursos curados por IA para tu tema</div>
    """, unsafe_allow_html=True)

    if not profile_exists(username):
        st.warning("Crea tu perfil primero para buscar recursos relacionados con tu tema.")
        if st.button("👤 Ir a mi perfil"):
            st.session_state.page = "profile"
            st.rerun()
        if st.button("⬅️ Volver al dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return

    profile = get_profile(username)
    topic = profile["topic"]

    st.markdown(f'<div class="rs-section">Tema: {topic}</div>', unsafe_allow_html=True)

    query = st.text_input(
        "¿Qué quieres aprender o reforzar?",
        placeholder=f"Ej: fundamentos de {topic}, ejercicios prácticos, conceptos avanzados...",
    )

    col_a, col_b = st.columns(2)
    do_search = col_a.button("🔍 Buscar recursos")
    do_reindex = col_b.button("🔄 Actualizar catálogo")

    if do_reindex:
        with st.spinner("🤖 El agente está curando recursos para tu tema..."):
            count = index_topic_resources(username, topic)
        if count:
            st.success(f"✅ Catálogo actualizado: {count} recursos indexados.")
            # Refrescar el catálogo mostrado y limpiar búsqueda previa
            st.session_state.rs_mode = "catalog"
            st.session_state.rs_results = get_topic_resources(username, topic, auto_index=False)
            st.session_state.rs_last_query = ""
        else:
            st.error("No se pudieron generar recursos. Intenta de nuevo.")

    if do_search:
        search_query = query.strip() or topic
        with st.spinner("Buscando los recursos más relevantes..."):
            results = search_resources(username, search_query, topic=topic)
        st.session_state.rs_mode = "search"
        st.session_state.rs_results = results
        st.session_state.rs_last_query = search_query

    # Si es la primera vez en la sesión (o no hay nada cargado), mostrar el catálogo completo
    if "rs_results" not in st.session_state:
        with st.spinner("Cargando tus recursos..."):
            st.session_state.rs_results = get_topic_resources(username, topic)
        st.session_state.rs_mode = "catalog"
        st.session_state.rs_last_query = ""

    results = st.session_state.get("rs_results")
    mode = st.session_state.get("rs_mode", "catalog")
    last_query = st.session_state.get("rs_last_query", "")

    if results:
        if mode == "search":
            st.markdown(f'<div class="rs-section">Resultados para: "{last_query}"</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="rs-section">Todos tus recursos</div>', unsafe_allow_html=True)
        st.markdown(_render_results(results), unsafe_allow_html=True)
    else:
        st.info("Aún no hay recursos. Usa «Actualizar catálogo» para generarlos.")

    if st.button("⬅️ Volver al dashboard"):
        # NO borramos rs_results: así al volver a entrar se recuerdan
        st.session_state.page = "dashboard"
        st.rerun()


def _render_results(results):
    icons = {
        "documentation": "📘",
        "course": "🎓",
        "video": "🎬",
        "tutorial": "💻",
        "book": "📚",
        "repository": "🐙",
        "article": "📖",
    }

    html = ""
    for r in results:
        icon = icons.get(r.get("type", "article"), "🔗")
        title = r.get("title", "Recurso")
        desc = r.get("description", "")
        url = r.get("url", "#")
        rtype = r.get("type", "article")
        level = r.get("level", "intermedio")
        relevance = r.get("relevance", None)

        # El badge de % solo aparece en resultados de búsqueda
        badge = f'<span class="rs-relevance">{relevance}% relevante</span>' if relevance is not None else ""

        html += f"""<div class="rs-card"><div class="rs-head"><span class="rs-icon">{icon}</span><span class="rs-rtitle">{title}</span>{badge}</div><div class="rs-desc">{desc}</div><div class="rs-meta"><span class="rs-tag">{rtype}</span><span class="rs-tag">{level}</span></div><a class="rs-link" href="{url}" target="_blank">🔗 Abrir recurso</a></div>"""

    return html