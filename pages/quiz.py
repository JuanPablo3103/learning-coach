import streamlit as st
from utils.agent import generate_quiz, load_learning_plan
from utils.profile import get_profile
from utils.database import save_quiz_result, get_quiz_history


def _reset_quiz_state():
    for k in ["quiz_data", "quiz_answers", "quiz_submitted", "quiz_topic"]:
        st.session_state.pop(k, None)


def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")

    st.markdown("""
    <style>
        .block-container { max-width: 620px !important; padding-top: 2.5rem !important; }
        .stApp { background: #0F0E1A !important; }
        .qz-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .qz-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .qz-section { font-size: 13px; color: rgba(255,255,255,0.5); font-weight: 500; margin: 1.5rem 0 0.5rem 0; }
        .qz-card { background: rgba(255,255,255,0.02); border: 0.5px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 1.1rem 1.25rem; margin-bottom: 1rem; }
        .qz-qnum { font-size: 11px; color: #A9A3E8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
        .qz-question { font-size: 15px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.6rem; }
        .qz-explain { font-size: 13px; color: rgba(255,255,255,0.5); margin-top: 0.5rem; padding: 8px 10px; background: rgba(83,74,183,0.08); border-left: 2px solid #534AB7; border-radius: 6px; }
        .qz-correct { color: #7FDD9E; font-weight: 500; }
        .qz-wrong { color: #DD7F7F; font-weight: 500; }
        .qz-history-row { display: flex; justify-content: space-between; align-items: center; padding: 9px 12px; background: rgba(255,255,255,0.02); border: 0.5px solid rgba(255,255,255,0.06); border-radius: 8px; margin-bottom: 6px; }
        .qz-history-topic { font-size: 13px; color: #E8E6F0; }
        .qz-history-score { font-size: 13px; color: #A9A3E8; font-weight: 500; }
        .qz-history-date { font-size: 11px; color: rgba(255,255,255,0.3); }
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
    <div class="qz-title">🧩 Quiz de Conocimiento</div>
    <div class="qz-sub">Pon a prueba lo que has aprendido con preguntas generadas por IA</div>
    """, unsafe_allow_html=True)

    # Tema por defecto: del plan, o del perfil como respaldo
    plan = load_learning_plan(username)
    profile = get_profile(username)
    default_topic = ""
    if plan and plan.get("topic"):
        default_topic = plan["topic"]
    elif profile and profile.get("topic"):
        default_topic = profile["topic"]

    # ── Estado 3: resultados ────────────────────────────────────────────
    if st.session_state.get("quiz_submitted"):
        _show_results(username)
        return

    # ── Estado 2: respondiendo ──────────────────────────────────────────
    if st.session_state.get("quiz_data"):
        _show_questions(username)
        return

    # ── Estado 1: configurar y generar ──────────────────────────────────
    if not default_topic:
        st.warning("Aún no tienes un tema definido. Crea tu perfil o genera un plan primero.")
        if st.button("👤 Ir a mi perfil"):
            st.session_state.page = "profile"
            st.rerun()
        if st.button("⬅️ Volver al dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return

    topic = st.text_input("Tema del quiz", value=default_topic)
    num_questions = st.slider("Número de preguntas", min_value=3, max_value=10, value=5)

    if st.button("🎯 Generar quiz"):
        with st.spinner("🤖 El agente está creando tus preguntas..."):
            quiz, message = generate_quiz(username, topic, num_questions)
        if quiz and quiz.get("questions"):
            st.session_state.quiz_data = quiz
            st.session_state.quiz_topic = topic
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()
        else:
            st.error(f"❌ {message}")

    _show_history(username)

    if st.button("⬅️ Volver al dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


def _show_questions(username):
    quiz = st.session_state.quiz_data
    questions = quiz["questions"]

    st.markdown(f'<div class="qz-section">Tema: {st.session_state.quiz_topic} · {len(questions)} preguntas</div>', unsafe_allow_html=True)

    answers = {}
    for i, q in enumerate(questions):
        st.markdown(f"""
        <div class="qz-card">
            <div class="qz-qnum">Pregunta {i + 1}</div>
            <div class="qz-question">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        options = q["options"]
        labels = [f"{k}) {v}" for k, v in options.items()]
        keys = list(options.keys())

        choice = st.radio(
            f"Selecciona una respuesta (pregunta {i + 1})",
            labels,
            index=None,
            key=f"quiz_q_{i}",
            label_visibility="collapsed",
        )
        if choice is not None:
            answers[i] = keys[labels.index(choice)]

    if st.button("✅ Enviar respuestas"):
        if len(answers) < len(questions):
            st.warning("Responde todas las preguntas antes de enviar.")
        else:
            st.session_state.quiz_answers = answers
            st.session_state.quiz_submitted = True
            st.rerun()

    if st.button("❌ Cancelar quiz"):
        _reset_quiz_state()
        st.rerun()


def _show_results(username):
    quiz = st.session_state.quiz_data
    questions = quiz["questions"]
    answers = st.session_state.quiz_answers
    topic = st.session_state.quiz_topic

    score = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["correct"])
    total = len(questions)
    pct = round(score / total * 100) if total else 0

    # Guardar resultado solo una vez
    if not st.session_state.get("quiz_saved"):
        save_quiz_result(username, topic, score, total)
        st.session_state.quiz_saved = True

    col1, col2, col3 = st.columns(3)
    col1.metric("Aciertos", score)
    col2.metric("Total", total)
    col3.metric("Puntaje", f"{pct}%")

    st.progress(pct / 100)

    if pct >= 80:
        st.success(f"¡Excelente! Dominas {topic}. 🚀")
    elif pct >= 50:
        st.info(f"Buen trabajo. Repasa los temas que fallaste para mejorar.")
    else:
        st.warning(f"Te recomiendo repasar {topic} antes de seguir avanzando.")

    st.markdown('<div class="qz-section">Revisión de respuestas</div>', unsafe_allow_html=True)

    for i, q in enumerate(questions):
        user_ans = answers.get(i)
        correct = q["correct"]
        options = q["options"]
        is_ok = user_ans == correct

        tu_resp = f'<span class="{"qz-correct" if is_ok else "qz-wrong"}">{user_ans}) {options[user_ans]}</span>'
        correcta = f'<span class="qz-correct">{correct}) {options[correct]}</span>'

        bloque = f"""
        <div class="qz-card">
            <div class="qz-qnum">Pregunta {i + 1} {"✅" if is_ok else "❌"}</div>
            <div class="qz-question">{q['question']}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.6);margin-bottom:4px;">Tu respuesta: {tu_resp}</div>
        """
        if not is_ok:
            bloque += f'<div style="font-size:13px;color:rgba(255,255,255,0.6);">Correcta: {correcta}</div>'
        if q.get("explanation"):
            bloque += f'<div class="qz-explain">💡 {q["explanation"]}</div>'
        bloque += "</div>"

        st.markdown(bloque, unsafe_allow_html=True)

    if st.button("🔄 Hacer otro quiz"):
        _reset_quiz_state()
        st.session_state.pop("quiz_saved", None)
        st.rerun()

    if st.button("⬅️ Volver al dashboard"):
        _reset_quiz_state()
        st.session_state.pop("quiz_saved", None)
        st.session_state.page = "dashboard"
        st.rerun()


def _show_history(username):
    history = get_quiz_history(username)
    if not history:
        return

    st.markdown('<div class="qz-section">Historial de quizzes</div>', unsafe_allow_html=True)

    rows_html = ""
    for h in history[:10]:
        pct = round(h["score"] / h["total"] * 100) if h["total"] else 0
        fecha = h["taken_at"].strftime("%d/%m/%Y") if h.get("taken_at") else ""
        rows_html += f"""<div class="qz-history-row"><span class="qz-history-topic">{h['topic']}</span><span class="qz-history-score">{h['score']}/{h['total']} · {pct}%</span><span class="qz-history-date">{fecha}</span></div>"""

    st.markdown(rows_html, unsafe_allow_html=True)