# PETdor2/backend/streamlit_app.py
import streamlit as st
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- IMPORTS RELATIVOS ---
from .auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
)

from .auth.password_reset import (
    solicitar_reset_senha,
    validar_token_reset,
    redefinir_senha_com_token
)

from .pages.cadastro_pet import render as cadastro_pet_app_render
from .pages.avaliacao import render as avaliacao_app_render
from .pages.login import render as login_app_render

# Configuração da página
st.set_page_config(page_title="PETDOR – Avaliação de Dor", layout="centered")
st.title("🐾 PETDOR – Sistema PETDOR")

# Inicializa session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Login"

# --- Lógica principal ---
if st.session_state.logged_in:
    st.sidebar.markdown("---")
    app_pages = {
        "Avaliação de Dor": avaliacao_app_render,
        "Cadastro de Pet": cadastro_pet_app_render,
    }

    if st.session_state.get("user_type") == "Admin":
        app_pages["Administração"] = None  # Substitua pelo app de administração

    selected_app_page = st.sidebar.selectbox(
        "Navegar",
        list(app_pages.keys()),
        index=list(app_pages.keys()).index(st.session_state.page) if st.session_state.page in app_pages else 0
    )
    st.session_state.page = selected_app_page

    if selected_app_page == "Avaliação de Dor":
        avaliacao_app_render()
    elif selected_app_page == "Cadastro de Pet":
        cadastro_pet_app_render()
    # elif selected_app_page == "Administração":
    #     admin_app()

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
else:
    login_app_render()

