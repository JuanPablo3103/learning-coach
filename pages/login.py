import streamlit as st
from utils.auth import login_user

def show():
    """Página de inicio de sesión.

    Muestra un formulario para que el usuario ingrese su nombre de usuario y contraseña.
    Incluye un botón para navegar a la página de registro.
    """
    st.title("🔐 Iniciar sesión")
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Acceder")
        if submitted:
            if username and password:
                success, result = login_user(username, password)
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["name"] = result  # nombre del usuario
                    st.session_state["page"] = "dashboard"
                    st.rerun()
                else:
                    st.error(f"❌ {result}")
            else:
                st.warning("Por favor ingresa usuario y contraseña")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("¿No tienes cuenta? Regístrate", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()
    with col2:
        if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
            st.session_state["page"] = "recover"
            st.rerun()
