import streamlit as st
from utils.agent import (
    load_learning_plan, generate_quiz, save_quiz_result,
    get_quiz_results, mark_task_completed, log_decision
)


def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")

    # ── Premium Styles ──
    st.markdown("""
    <style>
        .block-container { max-width: 680px !important; padding-top: 2rem !important; }
        .quiz-header { font-size: 22px; font-weight: 600; color: #E8E6F0; margin-bottom: 0.3rem; }
        .quiz-sub { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 1.5rem; }
        .quiz-score-card {
            background: linear-gradient(135deg, rgba(83,74,183,0.25), rgba(127,119,221,0.10));
            border: 1px solid rgba(83,74,183,0.3); border-radius: 14px;
            padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;
        }
        .quiz-score-big { font-size: 48px; font-weight: 700; color: #A9A3E8; }
        .quiz-score-label { font-size: 13px; color: rgba(255,255,255,0.4); margin-top: 4px; }
        .quiz-q-card {
            background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.08);
            border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;
        }
        .quiz-q-num { font-size: 11px; color: #7F77DD; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
        .quiz-q-text { font-size: 15px; color: #E8E6F0; margin-bottom: 0.8rem; line-height: 1.5; }
        .quiz-correct { color: #4ADE80; font-weight: 500; }
        .quiz-wrong { color: #F87171; font-weight: 500; }
        .history-row {
            display: flex; justify-content: space-between; align-items: center;
            padding: 0.7rem 1rem; border-bottom: 0.5px solid rgba(255,255,255,0.06);
        }
        .history-topic { font-size: 14px; color: #E8E6F0; }
        .history-score { font-size: 13px; font-weight: 600; }
        .history-date { font-size: 11px; color: rgba(255,255,255,0.3); }
    </style>
    <div class="quiz-header">📝 Quizzes de Evaluación</div>
    <div class="quiz-sub">Evalúa tu aprendizaje con preguntas generadas automáticamente</div>
    """, unsafe_allow_html=True)

    plan = load_learning_plan(username)
    if not plan:
        st.warning("⚠️ Primero genera tu plan de aprendizaje en la sección **Plan**.")
        return

    # ── Selector de tema ──
    options = []
    for week in plan.get("weeks", []):
        for day in week.get("days", []):
            label = f"Sem {week['week']} · {day['day']} — {day['topic']}"
            options.append((label, week["week"], day["day"], day["topic"]))

    if not options:
        st.info("No hay temas disponibles en tu plan.")
        return

    labels = [o[0] for o in options]
    choice = st.selectbox("Selecciona un tema para el quiz:", labels)
    idx = labels.index(choice)
    _, sel_week, sel_day, sel_topic = options[idx]

    # ── State keys ──
    qk = "quiz_questions"
    sk = "quiz_submitted"
    ak = "quiz_answers"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Generar Quiz", use_container_width=True):
            with st.spinner("Generando preguntas..."):
                questions, msg = generate_quiz(plan["topic"], sel_topic)
            st.session_state[qk] = questions
            st.session_state[sk] = False
            st.session_state[ak] = {}
            st.session_state["quiz_meta"] = (sel_week, sel_day, sel_topic)
            st.toast(msg)
            st.rerun()

    # ── Show quiz ──
    if qk in st.session_state and st.session_state[qk]:
        questions = st.session_state[qk]
        submitted = st.session_state.get(sk, False)

        st.markdown("---")
        answers = st.session_state.get(ak, {})

        for i, q in enumerate(questions):
            q_type = q.get("type", "multiple_choice")
            st.markdown(f"""
            <div class="quiz-q-card">
                <div class="quiz-q-num">Pregunta {i+1} · {'Opción Múltiple' if q_type == 'multiple_choice' else 'Verdadero / Falso'}</div>
                <div class="quiz-q-text">{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)

            if q_type == "multiple_choice":
                opts = q.get("options", [])
                if not submitted:
                    answers[i] = st.radio(
                        f"Respuesta {i+1}", opts,
                        index=None, key=f"q_{i}", label_visibility="collapsed"
                    )
                else:
                    user_ans_idx = opts.index(answers.get(i)) if answers.get(i) in opts else -1
                    correct_idx = q.get("correct", 0)
                    for j, opt in enumerate(opts):
                        if j == correct_idx:
                            st.markdown(f"✅ **{opt}**")
                        elif j == user_ans_idx and j != correct_idx:
                            st.markdown(f"❌ ~~{opt}~~")
                        else:
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{opt}")
            else:  # true_false
                if not submitted:
                    answers[i] = st.radio(
                        f"Respuesta {i+1}", ["Verdadero", "Falso"],
                        index=None, key=f"q_{i}", label_visibility="collapsed"
                    )
                else:
                    correct = q.get("correct", True)
                    user_val = answers.get(i)
                    user_bool = user_val == "Verdadero" if user_val else None
                    if correct:
                        st.markdown(f"✅ **Verdadero**")
                        if user_bool is False:
                            st.markdown(f"❌ ~~Tu respuesta: Falso~~")
                    else:
                        st.markdown(f"✅ **Falso**")
                        if user_bool is True:
                            st.markdown(f"❌ ~~Tu respuesta: Verdadero~~")

        st.session_state[ak] = answers

        if not submitted:
            if st.button("📤 Enviar Respuestas", use_container_width=True, type="primary"):
                # Score
                score = 0
                total = len(questions)
                for i, q in enumerate(questions):
                    user_a = answers.get(i)
                    if q["type"] == "multiple_choice":
                        opts = q.get("options", [])
                        correct_idx = q.get("correct", 0)
                        if user_a and opts.index(user_a) == correct_idx if user_a in opts else False:
                            score += 1
                    else:
                        correct_bool = q.get("correct", True)
                        user_bool = (user_a == "Verdadero") if user_a else None
                        if user_bool == correct_bool:
                            score += 1

                meta = st.session_state.get("quiz_meta", (1, "Lunes", ""))
                save_quiz_result(username, meta[0], meta[1], meta[2], score, total, answers)
                mark_task_completed(username, meta[0], meta[1])
                log_decision(username, "quiz_completed",
                             f"Quiz completado: {meta[2]} — {score}/{total}",
                             f"Semana {meta[0]}, {meta[1]}")

                st.session_state[sk] = True
                st.session_state["last_score"] = (score, total)
                st.rerun()
        else:
            score, total = st.session_state.get("last_score", (0, 0))
            pct = (score / total * 100) if total else 0
            color = "#4ADE80" if pct >= 70 else "#FBBF24" if pct >= 40 else "#F87171"
            st.markdown(f"""
            <div class="quiz-score-card">
                <div class="quiz-score-big" style="color:{color}">{score}/{total}</div>
                <div class="quiz-score-label">Puntuación: {pct:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Hacer otro quiz", use_container_width=True):
                for k in [qk, sk, ak, "quiz_meta", "last_score"]:
                    st.session_state.pop(k, None)
                st.rerun()

    # ── History ──
    st.markdown("---")
    st.markdown("### 📊 Historial de Quizzes")
    results = get_quiz_results(username)
    if results:
        for r in results[:10]:
            pct = (r["score"] / r["total"] * 100) if r["total"] else 0
            color = "#4ADE80" if pct >= 70 else "#FBBF24" if pct >= 40 else "#F87171"
            st.markdown(f"""
            <div class="history-row">
                <div>
                    <div class="history-topic">Sem {r['week']} · {r['day']} — {r['topic']}</div>
                    <div class="history-date">{r.get('created_at', '')}</div>
                </div>
                <div class="history-score" style="color:{color}">{r['score']}/{r['total']} ({pct:.0f}%)</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aún no has completado ningún quiz.")
