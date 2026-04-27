import streamlit as st
from utils.auth import get_security_question, verify_security_answer, update_password

def show():
    st.title("🔑 Recuperar contraseña")
    st.subheader("Sigue los pasos para recuperar tu cuenta")

    # Paso 1 — Ingresar usuario
    if "recover_step" not in st.session_state:
        st.session_state.recover_step = 1

    if st.session_state.recover_step == 1:
        st.markdown("### Paso 1 — Ingresa tu usuario")
        with st.form("recover_form_1"):
            username = st.text_input("👤 Usuario")
            submit = st.form_submit_button("Continuar")

        if submit:
            if not username:
                st.error("❌ Por favor ingresa tu usuario")
            else:
                question = get_security_question(username)
                if question is None:
                    st.error("❌ Usuario no encontrado")
                else:
                    st.session_state.recover_username = username
                    st.session_state.recover_step = 2
                    st.rerun()

    # Paso 2 — Responder pregunta de seguridad
    elif st.session_state.recover_step == 2:
        st.markdown("### Paso 2 — Responde tu pregunta de seguridad")
        question = get_security_question(st.session_state.recover_username)
        st.info(f"🔒 {question}")

        with st.form("recover_form_2"):
            answer = st.text_input("Tu respuesta", type="password")
            submit = st.form_submit_button("Verificar")

        if submit:
            if not answer:
                st.error("❌ Por favor ingresa tu respuesta")
            else:
                if verify_security_answer(st.session_state.recover_username, answer):
                    st.session_state.recover_step = 3
                    st.rerun()
                else:
                    st.error("❌ Respuesta incorrecta")

    # Paso 3 — Nueva contraseña
    elif st.session_state.recover_step == 3:
        st.markdown("### Paso 3 — Crea tu nueva contraseña")

        with st.form("recover_form_3"):
            new_password = st.text_input("🔒 Nueva contraseña", type="password")
            confirm_password = st.text_input("🔒 Confirmar contraseña", type="password")
            submit = st.form_submit_button("Actualizar contraseña")

        if submit:
            if not new_password or not confirm_password:
                st.error("❌ Por favor completa todos los campos")
            elif new_password != confirm_password:
                st.error("❌ Las contraseñas no coinciden")
            elif len(new_password) < 6:
                st.error("❌ La contraseña debe tener al menos 6 caracteres")
            else:
                update_password(st.session_state.recover_username, new_password)
                st.success("✅ Contraseña actualizada exitosamente")
                st.session_state.recover_step = 1
                st.session_state.recover_username = ""
                if st.button("Ir al login"):
                    st.session_state.page = "login"
                    st.rerun()

    st.markdown("---")
    if st.button("⬅️ Volver al login"):
        st.session_state.recover_step = 1
        st.session_state.page = "login"
        st.rerun()