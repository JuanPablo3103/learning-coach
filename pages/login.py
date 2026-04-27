import streamlit as st
from utils.auth import login_user

def show():
    st.title("🔐 Iniciar sesión")
    st.subheader("Bienvenido a tu coach de aprendizaje")

    with st.form("login_form"):
        username = st.text_input("👤 Usuario")
        password = st.text_input("🔒 Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")

    if submit:
        if not username or not password:
            st.error("❌ Por favor completa todos los campos")
        else:
            success, result = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.name = result
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error(f"❌ {result}")

    st.markdown("---")
    if st.button("¿No tienes cuenta? Regístrate"):
        st.session_state.page = "register"
        st.rerun()