 
import streamlit as st
from utils.auth import register_user

def show():
    st.title("📝 Crear cuenta")
    st.subheader("Regístrate para comenzar tu aprendizaje")

    with st.form("register_form"):
        name = st.text_input("👤 Nombre completo")
        username = st.text_input("👤 Usuario")
        email = st.text_input("📧 Correo electrónico")
        password = st.text_input("🔒 Contraseña", type="password")
        confirm_password = st.text_input("🔒 Confirmar contraseña", type="password")
        submit = st.form_submit_button("Registrarse")

    if submit:
        if not name or not username or not email or not password:
            st.error("❌ Por favor completa todos los campos")
        elif password != confirm_password:
            st.error("❌ Las contraseñas no coinciden")
        elif len(password) < 6:
            st.error("❌ La contraseña debe tener al menos 6 caracteres")
        else:
            success, message = register_user(username, name, password, email)
            if success:
                st.success("✅ Usuario registrado exitosamente")
                st.info("Ahora puedes iniciar sesión")
                if st.button("Ir al login"):
                    st.session_state.page = "login"
                    st.rerun()
            else:
                st.error(f"❌ {message}")

    st.markdown("---")
    if st.button("¿Ya tienes cuenta? Inicia sesión"):
        st.session_state.page = "login"
        st.rerun()