# PetDor2/streamlit_app.py
import sys
import os
import streamlit as st
import logging

# ===============================
# Configuração de logging
# ===============================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ===============================
# Ajuste correto do sys.path
# ===============================
# Caminho atual → /PETdor2/backend/streamlit_app.py
# Queremos adicionar /PETdor2/ ao sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
    logger.info(f"📂 BASE_DIR adicionado ao sys.path: {BASE_DIR}")

# ===============================
# Importações absolutas do backend
# ===============================
# Banco de dados
from backend.database import testar_conexao

# Autenticação
from backend.auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
    buscar_usuario_por_id,
)
from backend.auth.password_reset import (
    solicitar_reset_senha,
    redefinir_senha_com_token,
)
from backend.auth.email_confirmation import confirmar_email_com_token
from backend.auth.security import usuario_logado, logout, validar_token_reset_senha

# Páginas
from backend.pages.login import render as login_app_render
from backend.pages.cadastro import render as cadastro_app_render
from backend.pages.cadastro_pet import render as cadastro_pet_app_render
from backend.pages.avaliacao import render as avaliacao_app_render
from backend.pages.admin import render as admin_app_render
from backend.pages.home import render as home_app_render

# Utils
from backend.utils.config import APP_CONFIG, STREAMLIT_APP_URL

# ===============================
# Configurações Iniciais do Streamlit
# ===============================
st.set_page_config(
    page_title="PETDor - Avaliação de Dor Animal",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===============================
# Inicialização e Teste Supabase
# ===============================
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

if not st.session_state.db_connected:
    with st.spinner("Conectando ao banco de dados..."):
        sucesso, msg = testar_conexao()

        if sucesso:
            st.session_state.db_connected = True
            logger.info("✅ Conexão com Supabase estabelecida.")
        else:
            st.error("❌ Falha ao conectar ao Supabase.")
            st.error(msg)
            st.stop()

# ===============================
# Inicialização do Session State
# ===============================
default_states = {
    "logged_in": False,
    "user_id": None,
    "user_data": None,
    "page": "Login",
}

for key, value in default_states.items():
    st.session_state.setdefault(key, value)

# ===============================
# Tratamento de Query Params
# ===============================
query_params = st.query_params

if "action" in query_params and "token" in query_params:
    action = query_params["action"]
    token = query_params["token"]

    # --------- Confirmação de Email ---------
    if action == "confirm_email":
        st.subheader("Confirmando Email...")
        with st.spinner("Processando..."):
            sucesso, mensagem = confirmar_email_com_token(token)

        if sucesso:
            st.success(mensagem)
        else:
            st.error(mensagem)

        st.query_params.clear()
        st.session_state.page = "Login"
        st.rerun()

    # --------- Reset de Senha ---------
    elif action == "reset_password":
        st.subheader("Redefinir Senha")

        valido, email_do_token, msg = validar_token_reset_senha(token)

        if not valido:
            st.error(msg)
            st.query_params.clear()
            st.session_state.page = "Login"
            st.rerun()

        nova_senha = st.text_input("Nova senha", type="password")
        confirmar = st.text_input("Confirmar senha", type="password")

        if st.button("Redefinir"):
            if not nova_senha or not confirmar:
                st.error("Preencha todos os campos.")
            elif nova_senha != confirmar:
                st.error("As senhas não coincidem.")
            elif len(nova_senha) < 8:
                st.error("A senha deve ter no mínimo 8 caracteres.")
            else:
                sucesso, mensagem = redefinir_senha_com_token(token, nova_senha)
                if sucesso:
                    st.success(mensagem)
                    st.query_params.clear()
                    st.session_state.page = "Login"
                    st.rerun()
                else:
                    st.error(mensagem)

# ===============================
# Lógica da Interface
# ===============================
if usuario_logado(st.session_state):
    st.session_state.logged_in = True

    st.sidebar.title(f"Bem-vindo(a), {st.session_state.user_data.get('nome', 'Usuário')}")

    menu = ["Página Inicial", "Meus Pets e Avaliações", "Cadastro de Pet"]
    if st.session_state.user_data.get("tipo") == "Admin":
        menu.append("Administração")

    escolha = st.sidebar.selectbox("Navegação", menu)

    if escolha == "Página Inicial":
        home_app_render()
    elif escolha == "Meus Pets e Avaliações":
        avaliacao_app_render(st.session_state.user_data)
    elif escolha == "Cadastro de Pet":
        cadastro_pet_app_render(st.session_state.user_data)
    elif escolha == "Administração":
        admin_app_render(st.session_state.user_data)

    if st.sidebar.button("Sair"):
        logout(st.session_state)
        st.session_state.page = "Login"
        st.rerun()

else:
    st.session_state.logged_in = False

    st.sidebar.title("Acesso PETDor")
    opcao = st.sidebar.radio("Opções", ["Login", "Criar Conta", "Redefinir Senha"])

    if opcao == "Login":
        login_app_render()
    elif opcao == "Criar Conta":
        cadastro_app_render()
    elif opcao == "Redefinir Senha":
        st.subheader("Reset de Senha")
        email = st.text_input("Seu e-mail")

        if st.button("Enviar link"):
            if email:
                sucesso, mensagem = solicitar_reset_senha(email)
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)
            else:
                st.error("Digite um e-mail válido.")
