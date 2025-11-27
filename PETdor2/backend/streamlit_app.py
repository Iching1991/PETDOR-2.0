# PETdor2/backend/streamlit_app.py
import streamlit as st
import sys
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- INÍCIO DA CORREÇÃO DE IMPORTAÇÃO ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Adiciona o diretório 'backend' ao sys.path para importações absolutas dentro de 'backend'
if current_script_dir not in sys.path:
    sys.path.insert(0, current_script_dir)
# --- FIM DA CORREÇÃO DE IMPORTAÇÃO ---

# Importações corrigidas para corresponder aos nomes das funções
from auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
    confirmar_email,
)
from auth.password_reset import solicitar_reset_senha, validar_token_reset, redefinir_senha_com_token
from pages.cadastro_pet import render as cadastro_pet_app_render # Renomeado para evitar conflito
from pages.avaliacao import render as avaliacao_app_render # Renomeado para evitar conflito
from pages.login import render as login_app_render # Importa a função render da página de login

# 🔧 Inicializa banco (se houver uma migração via API REST)
# Se a migração for manual ou via SQL no Supabase, esta linha pode ser removida ou adaptada.
# migrar_banco_completo() # Remova ou comente esta linha

# Configuração da página
st.set_page_config(page_title="PETDOR – Avaliação de Dor", layout="centered")
st.title("🐾 PETDOR – Sistema PETDOR")

# Inicializa session_state se necessário
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Login" # Página inicial padrão

# --- Lógica principal do aplicativo ---
if st.session_state.logged_in:
    # Se o usuário está logado, mostra o menu lateral e as páginas do app
    st.sidebar.markdown("---")
    app_pages = {
        "Avaliação de Dor": avaliacao_app_render,
        "Cadastro de Pet": cadastro_pet_app_render,
    }

    if st.session_state.get("user_type") == "Admin":
        app_pages["Administração"] = None # Substitua None pela sua app de administração

    selected_app_page = st.sidebar.selectbox(
        "Navegar", 
        list(app_pages.keys()), 
        index=list(app_pages.keys()).index(st.session_state.page) if st.session_state.page in app_pages else 0
    )
    st.session_state.page = selected_app_page # Atualiza a página atual na sessão

    if selected_app_page == "Avaliação de Dor":
        avaliacao_app_render() # Chama a função render() da avaliação
    elif selected_app_page == "Cadastro de Pet":
        cadastro_pet_app_render()
    # elif selected_app_page == "Administração":
    #     admin_app()

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
else:
    # Se o usuário NÃO está logado, mostra a página de login
    login_app_render() # Chama a função render() da página de login
