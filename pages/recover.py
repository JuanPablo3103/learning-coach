import streamlit as st
from utils.auth import get_security_question, verify_security_answer, update_password

def show():
    st.markdown("""
    <style>
        .block-container { max-width: 460px !important; padding-top: 3rem !important; }
        .stApp { background: #0F0E1A !important; }
        .rec-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 2rem;
        }
        .rec-logo-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: #534AB7;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        .rec-logo-text { font-size: 16px; font-weight: 500; color: #E8E6F0; }
        .rec-logo-sub { font-size: 12px; color: rgba(255,255,255,0.35); }
        .rec-title { font-size: 22px; font-weight: 500; color: #E8E6F0; margin-bottom: 0.3rem; }
        .rec-subtitle { font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 2rem; }
        .steps {
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
        }
        .step-circle-active {
            width: 28px; height: 28px;
            border-radius: 50%;
            background: #534AB7;
            color: #EEEDFE;
            display: flex; align-items: center; justify-content: center;
            font-size: 12px; font-weight: 600;
            flex-shrink: 0;
        }
        .step-circle-done {
            width: 28px; height: 28px;
            border-radius: 50%;
            background: rgba(29,158,117,0.2);
            color: #1D9E75;
            border: 0.5px solid rgba(29,158,117,0.3);
            display: flex; align-items: center; justify-content: center;
            font-size: 12px; font-weight: 600;
            flex-shrink: 0;
        }
        .step-circle-inactive {
            width: 28px; height: 28px;
            border-radius: 50%;
            background: rgba(255,255,255,0.05);
            color: rgba(255,255,255,0.25);
            border: 0.5px solid rgba(255,255,255,0.08);
            display: flex; align-items: center; justify-content: center;
            font-size: 12px; font-weight: 600;
            flex-shrink: 0;
        }
        .step-label-active { font-size: 12px; color: #E8E6F0; margin-left: 6px; white-space: nowrap; }
        .step-label-inactive { font-size: 12px; color: rgba(255,255,255,0.3); margin-left: 6px; white-space: nowrap; }
        .step-line { flex: 1; height: 0.5px; background: rgba(255,255,255,0.08); margin: 0 8px; }
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
        .stFormSubmitButton > button:hover { background: #3C3489 !important; }
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
        .security-info {
            background: rgba(83,74,183,0.1);
            border: 0.5px solid rgba(83,74,183,0.25);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            color: #A9A3E8;
            margin-bottom: 1.25rem;
        }
        .success-box {
            background: rgba(29,158,117,0.1);
            border: 0.5px solid rgba(29,158,117,0.25);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            color: #1D9E75;
            margin-bottom: 1.25rem;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    if "recover_step" not in st.session_state:
        st.session_state.recover_step = 1

    step = st.session_state.recover_step

    def step_circle(num):
        if num < step:
            return f'<div class="step-circle-done">✓</div><span class="step-label-active">'
        elif num == step:
            return f'<div class="step-circle-active">{num}</div><span class="step-label-active">'
        else:
            return f'<div class="step-circle-inactive">{num}</div><span class="step-label-inactive">'

    labels = ["Usuario", "Seguridad", "Nueva clave"]

    steps_html = '<div class="steps">'
    for i, label in enumerate(labels, 1):
        steps_html += f'<div style="display:flex;align-items:center;">{step_circle(i)}{label}</span></div>'
        if i < 3:
            steps_html += '<div class="step-line"></div>'
    steps_html += '</div>'

    st.markdown(f"""
    <div class="rec-logo">
        <div class="rec-logo-icon">🧠</div>
        <div>
            <div class="rec-logo-text">Learning Coach</div>
            <div class="rec-logo-sub">Tu coach de aprendizaje con IA</div>
        </div>
    </div>
    <div class="rec-title">Recuperar contraseña</div>
    <div class="rec-subtitle">Sigue los pasos para recuperar tu cuenta.</div>
    {steps_html}
    """, unsafe_allow_html=True)

    if step == 1:
        with st.form("recover_form_1"):
            username = st.text_input("Usuario", placeholder="tu_usuario")
            submit = st.form_submit_button("Continuar →")
        if submit:
            if not username:
                st.error("Por favor ingresa tu usuario")
            else:
                question = get_security_question(username)
                if question is None:
                    st.error("Usuario no encontrado")
                else:
                    st.session_state.recover_username = username
                    st.session_state.recover_step = 2
                    st.rerun()

    elif step == 2:
        question = get_security_question(st.session_state.recover_username)
        st.markdown(f'<div class="security-info">🔒 {question}</div>', unsafe_allow_html=True)
        with st.form("recover_form_2"):
            answer = st.text_input("Tu respuesta", placeholder="••••••••", type="password")
            submit = st.form_submit_button("Verificar →")
        if submit:
            if not answer:
                st.error("Por favor ingresa tu respuesta")
            else:
                if verify_security_answer(st.session_state.recover_username, answer):
                    st.session_state.recover_step = 3
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta")

    elif step == 3:
        with st.form("recover_form_3"):
            new_password = st.text_input("Nueva contraseña", placeholder="••••••••", type="password")
            confirm_password = st.text_input("Confirmar contraseña", placeholder="••••••••", type="password")
            submit = st.form_submit_button("Actualizar contraseña")
        if submit:
            if not new_password or not confirm_password:
                st.error("Por favor completa todos los campos")
            elif new_password != confirm_password:
                st.error("Las contraseñas no coinciden")
            elif len(new_password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres")
            else:
                update_password(st.session_state.recover_username, new_password)
                st.markdown('<div class="success-box">✅ Contraseña actualizada exitosamente</div>', unsafe_allow_html=True)
                st.session_state.recover_step = 1
                st.session_state.recover_username = ""

    if st.button("← Volver al login"):
        st.session_state.recover_step = 1
        st.session_state.page = "login"
        st.rerun()