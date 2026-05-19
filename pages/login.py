import streamlit as st
from utils.auth import login_user

def show():
    st.markdown("""
    <style>
        .block-container {
            max-width: 460px !important;
            padding-top: 4rem !important;
        }
        .login-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 2rem;
        }
        .login-logo-icon {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            background: #534AB7;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
        }
        .login-logo-text {
            font-size: 16px;
            font-weight: 600;
            color: inherit;
        }
        .login-logo-sub {
            font-size: 12px;
            opacity: 0.5;
        }
        .login-title {
            font-size: 26px;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        .login-subtitle {
            font-size: 14px;
            opacity: 0.55;
            margin-bottom: 2rem;
        }
        div[data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        .stTextInput > label {
            font-size: 13px !important;
            opacity: 0.7;
        }
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 0.5px solid rgba(128,128,128,0.3) !important;
            padding: 10px 14px !important;
            font-size: 14px !important;
        }
        .stFormSubmitButton > button {
            width: 100% !important;
            background: #534AB7 !important;
            color: #EEEDFE !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 11px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin-top: 0.5rem !important;
        }
        .stFormSubmitButton > button:hover {
            background: #3C3489 !important;
        }
        .divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 1.5rem 0;
        }
        .divider span {
            font-size: 12px;
            opacity: 0.4;
        }
        .divider::before, .divider::after {
            content: '';
            flex: 1;
            height: 0.5px;
            background: rgba(128,128,128,0.3);
        }
        .stButton > button {
            border-radius: 8px !important;
            border: 0.5px solid rgba(128,128,128,0.3) !important;
            font-size: 13px !important;
            color: inherit !important;
            background: transparent !important;
        
        }
        .stApp {
                background: #0F0E1A !important;
        }
        .stButton > button:hover {
            border-color: #534AB7 !important;
            color: #534AB7 !important;
        }
                
    </style>

    <div class="login-logo">
        <div class="login-logo-icon">🧠</div>
        <div>
            <div class="login-logo-text">Learning Coach</div>
            <div class="login-logo-sub">Tu coach de aprendizaje con IA</div>
        </div>
    </div>

    <div class="login-title">Iniciar sesión</div>
    <div class="login-subtitle">Bienvenido de nuevo. Continúa tu camino de aprendizaje.</div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="tu_usuario")
        password = st.text_input("Contraseña", placeholder="••••••••", type="password")
        submit = st.form_submit_button("Iniciar sesión")

    if submit:
        if not username or not password:
            st.error("Por favor completa todos los campos")
        else:
            success, result = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.name = result
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error(f"{result}")

    st.markdown('<div class="divider"><span>o</span></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("¿No tienes cuenta? Regístrate", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
    with col2:
        if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
            st.session_state.page = "recover"
            st.rerun()