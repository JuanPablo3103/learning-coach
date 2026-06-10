import streamlit as st
from pages import login, register, dashboard, recover, profile, plan, roadmap, stats, negotiate, quiz, resources
from utils.database import init_db

init_db()

st.set_page_config(
    page_title="Personal Learning Coach",
    page_icon="🎓",
    layout="centered"
)

# Estilos globales (se aplican a TODAS las páginas)
st.markdown("""
    <style>
        /* Ocultar menú de Streamlit */
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* Botones tipo "tarjeta" consistentes en toda la app.
           El selector .stApp lo hace más específico que el de cada página,
           así gana sin necesidad de editar archivo por archivo. */
        .stApp .stButton > button {
            width: 100% !important;
            background: rgba(255,255,255,0.04) !important;
            border: 0.5px solid rgba(255,255,255,0.09) !important;
            border-radius: 12px !important;
            color: #E8E6F0 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 0.8rem 1rem !important;
            transition: all 0.15s ease !important;
        }
        .stApp .stButton > button:hover {
            border-color: #534AB7 !important;
            background: rgba(83,74,183,0.15) !important;
            color: #FFFFFF !important;
        }
        .stApp .stButton > button:focus:not(:active) {
            border-color: #534AB7 !important;
            color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "name" not in st.session_state:
    st.session_state.name = ""

# Navegación entre páginas
if st.session_state.logged_in:
    if st.session_state.page not in ["dashboard", "profile", "plan", "roadmap", "stats", "negotiate", "quiz", "resources"]:
        st.session_state.page = "dashboard"

if st.session_state.page == "login":
    login.show()
elif st.session_state.page == "register":
    register.show()
elif st.session_state.page == "recover":
    recover.show()
elif st.session_state.page == "dashboard":
    dashboard.show()
elif st.session_state.page == "profile":
    profile.show()
elif st.session_state.page == "plan":
    plan.show()
elif st.session_state.page == "roadmap":
    roadmap.show()
elif st.session_state.page == "stats":
    stats.show()
elif st.session_state.page == "negotiate":
    negotiate.show()
elif st.session_state.page == "quiz":
    quiz.show()
elif st.session_state.page == "resources":
    resources.show()