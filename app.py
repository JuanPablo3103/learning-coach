import streamlit as st
from utils.database import init_db

# Inicializar la base de datos (PostgreSQL o SQLite fallback)
init_db()

# Configuración estética de la página
st.set_page_config(
    page_title="Personal Learning Coach",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Ocultar barra de menú y footer de Streamlit para un look premium
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stSidebarNav"] {display: none !important;}
        .stApp {background: #0F0E1A; color: #E8E6F0;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Estado de sesión inicial
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# Navegación cuando el usuario está autenticado
if st.session_state.logged_in:
    st.sidebar.title("🤖 Learning Coach")
    st.session_state.page = st.sidebar.radio(
        "Navegar",
        ["dashboard", "profile", "plan", "quiz", "resources", "roadmap"]
    )

# Enrutamiento de páginas
page = st.session_state.page

if page == "login":
    from pages.login import show as login_show
    login_show()
elif page == "register":
    from pages.register import show as register_show
    register_show()
elif page == "recover":
    from pages.recover import show as recover_show
    recover_show()
elif page == "dashboard":
    from pages.dashboard import show as dashboard_show
    dashboard_show()
elif page == "profile":
    from pages.profile import show as profile_show
    profile_show()
elif page == "plan":
    from pages.plan import show as plan_show
    plan_show()
elif page == "quiz":
    from pages.quiz import show as quiz_show
    quiz_show()
elif page == "resources":
    from pages.resources_page import show as resources_show
    resources_show()
elif page == "roadmap":
    from pages.roadmap import show as roadmap_show
    roadmap_show()
