import streamlit as st
from utils.auth import register_user_with_security

SECURITY_QUESTIONS = [
    "¿Cuál es el nombre de tu primera mascota?",
    "¿En qué ciudad naciste?",
    "¿Cuál es el nombre de tu mejor amigo de la infancia?",
    "¿Cuál es el nombre de tu escuela primaria?",
    "¿Cuál es tu comida favorita?"
]

def show():
    st.title("📝 Crear cuenta")
    st.subheader("Regístrate para comenzar tu aprendizaje")

    with st.form("register_form"):
        name = st.text_input("👤 Nombre completo")
        username = st.text_input("👤 Usuario")
        email = st.text_input("📧 Correo electrónico")
        password = st.text_input("🔒 Contraseña", type="password")
        confirm_password = st.text_input("🔒 Confirmar contraseña", type="password")
        
        st.markdown("---")
        st.subheader("🔑 Pregunta de seguridad")
        security_question = st.selectbox("Selecciona una pregunta", SECURITY_QUESTIONS)
        security_answer = st.text_input("Tu respuesta", type="password")
        
        submit = st.form_submit_button("Registrarse")

    if submit:
        if not name or not username or not email or not password or not security_answer:
            st.error("❌ Por favor completa todos los campos")
        elif password != confirm_password:
            st.error("❌ Las contraseñas no coinciden")
        elif len(password) < 6:
            st.error("❌ La contraseña debe tener al menos 6 caracteres")
        else:
            success, message = register_user_with_security(
                username, name, password, email,
                security_question, security_answer
            )
            if success:
                st.success("✅ Usuario registrado exitosamente")
                st.info("Ahora puedes iniciar sesión")
            else:
                st.error(f"❌ {message}")

    st.markdown("---")
    if st.button("¿Ya tienes cuenta? Inicia sesión"):
        st.session_state.page = "login"
        st.rerun()