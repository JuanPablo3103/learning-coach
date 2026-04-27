import streamlit as st
from utils.agent import generate_learning_plan, save_learning_plan, load_learning_plan

def show():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    username = st.session_state.get("username")
    st.title("📅 Mi Plan de Aprendizaje")
    st.markdown("---")

    # Verificar si ya tiene un plan
    existing_plan = load_learning_plan(username)

    if existing_plan:
        show_plan(existing_plan)
        st.markdown("---")
        if st.button("🔄 Generar nuevo plan"):
            st.session_state.generating = True
            st.rerun()
    else:
        st.session_state.generating = True

    if st.session_state.get("generating"):
        generate_plan(username)

    st.markdown("---")
    if st.button("⬅️ Volver al dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

def generate_plan(username):
    st.info("🤖 El agente está generando tu plan personalizado...")
    with st.spinner("Analizando tu perfil y generando el plan..."):
        plan, message = generate_learning_plan(username)

    if plan:
        save_learning_plan(username, plan)
        st.session_state.generating = False
        st.success("✅ Plan generado exitosamente")
        st.rerun()
    else:
        st.error(f"❌ {message}")
        st.session_state.generating = False

def show_plan(plan):
    st.subheader(f"📚 Tema: {plan['topic']}")
    st.write(f"⏱️ Duración: {plan['duration_weeks']} semanas")
    st.write(f"🕐 Horas por semana: {plan['weekly_hours']} horas/día")

    st.markdown("---")

    for week in plan['weeks']:
        with st.expander(f"📅 Semana {week['week']} — {week['title']}"):
            st.write(f"🎯 **Objetivo:** {week['objective']}")
            st.markdown("---")
            for day in week['days']:
                st.markdown(f"### 📆 {day['day']}")
                st.write(f"📖 **Tema:** {day['topic']}")
                st.write(f"⏰ **Duración:** {day['duration_hours']} horas")
                st.markdown("**📎 Recursos:**")
                for resource in day['resources']:
                    st.markdown(f"- [{resource['title']}]({resource['url']}) — {resource['type']} ({resource['duration_minutes']} min)")
                st.markdown("---")