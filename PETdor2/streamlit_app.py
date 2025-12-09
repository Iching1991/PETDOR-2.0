# PetDor2/streamlit_app.py
import streamlit as st
import sys
import os
import logging

# ===============================
# Configuração de logging
# ===============================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ===============================
# Ajuste do sys.path para imports absolutos
# ===============================
# Adiciona o diretório raiz do projeto (PETdor2/) ao sys.path
# Isso permite importar módulos como 'backend.auth.user' ou 'backend.pages.login'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ===============================
# Importações absolutas a partir do pacote 'backend'
# ===============================
from backend.database import testar_conexao # Importa do pacote database
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
from backend.pages.login import render as login_app_render
from backend.pages.cadastro import render as cadastro_app_render
from backend.pages.cadastro_pet import render as cadastro_pet_app_render
from backend.pages.avaliacao import render as avaliacao_app_render
from backend.pages.admin import render as admin_app_render
from backend.pages.home import render as home_app_render # Corrigido para render como home_app_render
from backend.pages.sobre import render as sobre_app_render # Assumindo que sobre.py tem render()
from backend.utils.config import APP_CONFIG, STREAMLIT_APP_URL # Para URLs de e-mail

# ===============================
# Configuração da Página Streamlit
# ===============================
st.set_page_config(
    page_title="PetDor 2.0",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# Inicialização do Session State
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "page" not in st.session_state:
    st.session_state.page = "Login" # Página padrão
if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = False

# ===============================
# Teste de Conexão com Supabase (apenas uma vez)
# ===============================
if not st.session_state.db_initialized:
    with st.spinner("Conectando ao Supabase..."):
        if testar_conexao():
            st.session_state.db_initialized = True
            logger.info("✅ Conexão com Supabase estabelecida.")
        else:
            st.error("❌ Falha ao conectar ao Supabase. Verifique as variáveis de ambiente.")
            st.stop() # Para a execução se não conseguir conectar

# ===============================
# Processamento de Query Parameters (Confirmação/Reset de E-mail)
# ===============================
query_params = st.query_params

if "action" in query_params and "token" in query_params:
    action = query_params["action"]
    token = query_params["token"]

    if action == "confirm_email":
        st.subheader("Confirmação de E-mail")
        with st.spinner("Confirmando seu e-mail..."):
            sucesso, mensagem = confirmar_email_com_token(token)
            if sucesso:
                st.success(mensagem)
                st.info("Você pode fazer login agora.")
            else:
                st.error(mensagem)
        # Limpa os query params para evitar reprocessamento
        st.query_params.clear()
        st.session_state.page = "Login" # Redireciona para login
        st.rerun()

    elif action == "reset_password":
        st.subheader("Redefinir Senha")
        with st.spinner("Validando token..."):
            valido, email_do_token, msg_validacao = validar_token_reset_senha(token)

            if valido and email_do_token:
                st.success(msg_validacao)
                nova_senha = st.text_input("Nova Senha", type="password", key="reset_nova_senha")
                confirmar_nova_senha = st.text_input("Confirmar Nova Senha", type="password", key="reset_confirmar_senha")

                if st.button("Redefinir Senha"):
                    if not nova_senha or not confirmar_nova_senha:
                        st.error("Por favor, preencha todos os campos de senha.")
                    elif nova_senha != confirmar_nova_senha:
                        st.error("As senhas não coincidem.")
                    elif len(nova_senha) < 8:
                        st.error("A senha deve ter pelo menos 8 caracteres.")
                    else:
                        sucesso_reset, msg_reset = redefinir_senha_com_token(token, nova_senha)
                        if sucesso_reset:
                            st.success(msg_reset)
                            st.info("Sua senha foi redefinida. Você pode fazer login agora.")
                            st.query_params.clear()
                            st.session_state.page = "Login"
                            st.rerun()
                        else:
                            st.error(msg_reset)
            else:
                st.error(msg_validacao)
        # Limpa os query params após a tentativa de reset, mesmo que falhe
        st.query_params.clear()
        st.session_state.page = "Login" # Redireciona para login
        st.rerun()

# ===============================
# Lógica Principal do Aplicativo
# ===============================
if usuario_logado(st.session_state):
    st.session_state.logged_in = True # Garante que o estado está correto

    # Menu lateral para usuários logados
    menu_options = ["Página Inicial", "Meus Pets e Avaliações", "Cadastro de Pet"]
    if st.session_state.user_data and st.session_state.user_data.get("is_admin"): # Verifica a coluna 'is_admin'
        menu_options.append("Administração")
    menu_options.append("Sobre") # Adiciona "Sobre" para todos os usuários logados

    st.sidebar.title(f"Bem-vindo(a), {st.session_state.user_data.get('nome', 'Usuário')}!")
    selected_page = st.sidebar.selectbox("Navegação", menu_options, key="logged_in_menu")

    if selected_page == "Página Inicial":
        home_app_render(st.session_state.user_data) # Passa user_data para a home
    elif selected_page == "Meus Pets e Avaliações":
        avaliacao_app_render(st.session_state.user_data)
    elif selected_page == "Cadastro de Pet":
        cadastro_pet_app_render(st.session_state.user_data)
    elif selected_page == "Administração":
        admin_app_render(st.session_state.user_data)
    elif selected_page == "Sobre":
        sobre_app_render()
    else:
        st.error("Página não encontrada ou não implementada.")

    if st.sidebar.button("Sair"):
        logout(st.session_state)
        st.session_state.page = "Login" # Redireciona para login
        st.rerun()

else:
    st.session_state.logged_in = False
    # Menu lateral para usuários não logados
    st.sidebar.title("Acesso PETDor")
    selected_option = st.sidebar.radio("Opções", ["Login", "Criar Conta", "Redefinir Senha", "Sobre"], key="logged_out_menu")

    if selected_option == "Login":
        login_app_render()
    elif selected_option == "Criar Conta":
        cadastro_app_render()
    elif selected_option == "Redefinir Senha":
        st.subheader("Redefinir Senha")
        email_reset = st.text_input("Digite seu e-mail para resetar a senha:", key="forgot_password_email")
        if st.button("Enviar link de reset"):
            if email_reset:
                sucesso, mensagem = solicitar_reset_senha(email_reset)
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)
            else:
                st.error("Por favor, digite um e-mail.")
    elif selected_option == "Sobre":
        sobre_app_render()
    else:
        # Caso padrão para evitar estado vazio
        st.session_state.page = "Login"
        login_app_render()
