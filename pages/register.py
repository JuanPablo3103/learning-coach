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
    st.markdown("""
    <style>
        .block-container { max-width: 500px !important; padding-top: 3rem !important; }
        .stApp { background: #0F0E1A !important; }
        .reg-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 2rem;
        }
        .reg-logo-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: #534AB7;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        .reg-logo-text { font-size: 16px; font-weight: 500; color: #E8E6F0; }
        .reg-logo-sub { font-size: 12px; color: rgba(255,255,255,0.35); }
        .reg-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .reg-subtitle { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .reg-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 1.25rem 0;
        }
        .reg-divider span {
            font-size: 11px;
            color: rgba(255,255,255,0.25);
            white-space: nowrap;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .reg-divider::before, .reg-divider::after {
            content: '';
            flex: 1;
            height: 0.5px;
            background: rgba(255,255,255,0.08);
        }
        div[data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        .stTextInput > label {
            font-size: 12px !important;
            color: rgba(255,255,255,0.45) !important;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }
        .stSelectbox > label {
            font-size: 12px !important;
            color: rgba(255,255,255,0.45) !important;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 0.5px solid rgba(255,255,255,0.1) !important;
            background: rgba(255,255,255,0.05) !important;
            color: #E8E6F0 !important;
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
        .stButton > button {
            width: 100% !important;
            background: transparent !important;
            border: 0.5px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
            color: rgba(255,255,255,0.4) !important;
            font-size: 13px !important;
            margin-top: 0.5rem !important;
        }
        .stButton > button:hover {
            border-color: #534AB7 !important;
            color: #7F77DD !important;
        }
    </style>

    <div class="reg-logo">
        <div class="reg-logo-icon">🧠</div>
        <div>
            <div class="reg-logo-text">Learning Coach</div>
            <div class="reg-logo-sub">Tu coach de aprendizaje con IA</div>
        </div>
    </div>
    <div class="reg-title">Crear cuenta</div>
    <div class="reg-subtitle">Regístrate para comenzar tu camino de aprendizaje.</div>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre completo", placeholder="Juan Pablo")
        with col2:
            username = st.text_input("Usuario", placeholder="jpablo")

        email = st.text_input("Correo electrónico", placeholder="juan@gmail.com")

        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Contraseña", placeholder="••••••••", type="password")
        with col4:
            confirm_password = st.text_input("Confirmar contraseña", placeholder="••••••••", type="password")

        st.markdown('<div class="reg-divider"><span>Pregunta de seguridad</span></div>', unsafe_allow_html=True)

        security_question = st.selectbox("Selecciona una pregunta", SECURITY_QUESTIONS)
        security_answer = st.text_input("Tu respuesta", placeholder="••••••••", type="password")

        submit = st.form_submit_button("Crear cuenta")

    if submit:
        if not name or not username or not email or not password or not security_answer:
            st.error("Por favor completa todos los campos")
        elif password != confirm_password:
            st.error("Las contraseñas no coinciden")
        elif len(password) < 6:
            st.error("La contraseña debe tener al menos 6 caracteres")
        else:
            success, message = register_user_with_security(
                username, name, password, email,
                security_question, security_answer
            )
            if success:
                st.success("Usuario registrado exitosamente")
                st.info("Ahora puedes iniciar sesión")
            else:
                st.error(message)

    if st.button("¿Ya tienes cuenta? Inicia sesión"):
        st.session_state.page = "login"
        st.rerun()