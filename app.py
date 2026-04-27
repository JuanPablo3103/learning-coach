import streamlit as st
from pages import login, register, dashboard

st.set_page_config(
    page_title="Personal Learning Coach",
    page_icon="🎓",
    layout="centered"
)

# Ocultar menú de Streamlit
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
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
    st.session_state.page = "dashboard"

if st.session_state.page == "login":
    login.show()
elif st.session_state.page == "register":
    register.show()
elif st.session_state.page == "dashboard":
    dashboard.show()