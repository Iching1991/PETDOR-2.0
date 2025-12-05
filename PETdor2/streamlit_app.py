# ================================================
#  streamlit_app.py (refatorado)
#  PETdor2/streamlit_app.py
# ================================================
import os
import sys
import logging
import streamlit as st

# ========================================================
# 🛠 CONFIGURAÇÃO DE LOG
# ========================================================
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ========================================================
# 🛠 AJUSTE DO sys.path PARA PERMITIR "backend.*"
# ========================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # → PETdor2/

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
    logger.info(f"📌 BASE_DIR adicionado ao sys.path: {BASE_DIR}")

# ========================================================
# 🛠 IMPORTS DO BACKEND (AGORA FUNCIONAM)
# ========================================================

# Banco de Dados
from PETdor2.backend.database import testar_conexao

# Autenticação
from backend.auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_id,
)
from backend.auth.password_reset import (
    solicitar_reset_senha,
    redefinir_senha_com_token,
)
from backend.auth.email_confirmation import confirmar_email_com_token
from backend.auth.security import usuario_logado, logout, validar_token_reset_senha

# Páginas do sistema
from backend.pages.login import render as login_app_render
from backend.pages.cadastro import render as cadastro_app_render
from backend.pages.cadastro_pet import render as cadastro_pet_app_render
from backend.pages.avaliacao import render as avaliacao_app_render
from backend.pages.admin import render as admin_app_render
from backend.pages.home import render as home_app_render

# Configurações gerais
from backend.utils.config import APP_CONFIG, STREAMLIT_APP_URL

# ========================================================
# 🎨 CONFIGURAÇÕES DO STREAMLIT
# ========================================================
st.set_page_config(
    page_title="PETDor - Avaliação de Dor Animal",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========================================================
# 🔌 TESTE DE CONEXÃO COM O BANCO (Supabase)
# ========================================================
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

if not st.session_state.db_connected:
    with st.spinner("Conectando ao banco de dados..."):
        ok, msg = testar_conexao()
        if ok:
            st.session_state.db_connected = True
            logger.info("✅ Supabase conectado com sucesso!")
        else:
            st.error("❌ Falha ao conectar ao Supabase.")
            st.error(msg)
            st.stop()

# ========================================================
# 🔐 ESTADOS PADRÃO DA SESSÃO
# ========================================================
default_states = {
    "logged_in": False,
    "user_id": None,
    "user_data": None,
    "page": "Login",
}

for key, value in default_states.items():
    st.session_state.setdefault(key, value)

# ========================================================
# 🔗 TRATAMENTO DE QUERY PARAMS (email / reset senha)
# ========================================================
query = st.query_params

# -------- Confirmação de email --------
if query.get("action") == "confirm_email" and "token" in query:
    token = query["token"]

    st.subheader("Confirmando Email...")
    with st.spinner("Processando..."):
        sucesso, mensagem = confirmar_email_com_token(token)

    st.success(mensagem) if sucesso else st.error(mensagem)

    st.query_params.clear()
    st.session_state.page = "Login"
    st.rerun()

# -------- Reset de senha --------
if query.get("action") == "reset_password" and "token" in query:
    token = query["token"]

    st.subheader("Redefinir Senha")

    valido, email_token, msg = validar_token_reset_senha(token)
    if not valido:
        st.error(msg)
        st.query_params.clear()
        st.session_state.page = "Login"
        st.rerun()

    nova = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    if st.button("Redefinir senha"):
        if not nova or not confirmar:
            st.error("Preencha os campos.")
        elif nova != confirmar:
            st.error("As senhas não coincidem.")
        elif len(nova) < 8:
            st.error("A senha deve ter pelo menos 8 caracteres.")
        else:
            ok, mensagem = redefinir_senha_com_token(token, nova)
            if ok:
                st.success(mensagem)
                st.query_params.clear()
                st.session_state.page = "Login"
                st.rerun()
            else:
                st.error(mensagem)

# ========================================================
# 🧭 ROTEAMENTO PRINCIPAL
# ========================================================
if usuario_logado(st.session_state):
    st.session_state.logged_in = True
    user = st.session_state.user_data

    st.sidebar.title(f"Bem-vindo(a), {user.get('nome', 'Usuário')}")

    menu = ["Página Inicial", "Meus Pets e Avaliações", "Cadastro de Pet"]
    if user.get("is_admin", False):
        menu.append("Administração")

    escolha = st.sidebar.selectbox("Navegação", menu)

    if escolha == "Página Inicial":
        home_app_render()
    elif escolha == "Meus Pets e Avaliações":
        avaliacao_app_render(user)
    elif escolha == "Cadastro de Pet":
        cadastro_pet_app_render(user)
    elif escolha == "Administração":
        admin_app_render(user)

    if st.sidebar.button("Sair"):
        logout(st.session_state)
        st.session_state.page = "Login"
        st.rerun()

# ========================================================
# 🔓 USUÁRIO NÃO LOGADO
# ========================================================
else:
    st.session_state.logged_in = False

    st.sidebar.title("Acesso PETDor")
    opcao = st.sidebar.radio("Menu", ["Login", "Criar Conta", "Redefinir Senha"])

    if opcao == "Login":
        login_app_render()

    elif opcao == "Criar Conta":
        cadastro_app_render()

    elif opcao == "Redefinir Senha":
        st.subheader("Reset de Senha")
        email = st.text_input("Digite seu e-mail")

        if st.button("Enviar link"):
            if not email:
                st.error("Digite um e-mail.")
            else:
                ok, msg = solicitar_reset_senha(email)
                st.success(msg) if ok else st.error(msg)
