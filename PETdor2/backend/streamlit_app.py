# PETdor2/backend/streamlit_app.py
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
# Ajuste do sys.path para imports absolutos
# ===============================
# Adiciona o diretório 'backend' ao sys.path para que as importações absolutas funcionem
# Isso permite importar módulos como 'auth.user' ou 'pages.login'
# sem problemas de "top-level package".
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# ===============================
# Importações absolutas a partir do pacote 'backend'
# ===============================
# Módulos de Autenticação e Usuário
from auth.user import (
    buscar_usuario_por_email, verificar_credenciais, cadastrar_usuario,
    atualizar_tipo_usuario, atualizar_status_usuario, redefinir_senha # redefinir_senha agora vem de auth.user
)
from auth.security import (
    gerar_token_reset_senha, validar_token_reset_senha,
    gerar_token_confirmacao_email, validar_token_confirmacao_email,
    hash_password, verify_password # Nomes corretos das funções de hash
)
from auth.password_reset import solicitar_reset_senha, redefinir_senha_com_token # Importa funções específicas de reset
from auth.email_confirmation import enviar_email_confirmacao_usuario

# Módulos de Páginas
from pages.login import render as login_app_render
from pages.cadastro import render as cadastro_app_render
from pages.cadastro_pet import render as cadastro_pet_app_render
from pages.avaliacao import render as avaliacao_app_render
from pages.admin import render as admin_app_render # Página de administração

# Módulos de Banco de Dados e Configurações
from database.supabase_client import testar_conexao # Para testar a conexão com Supabase
from database.migrations import migrar_colunas_desativacao # Para migrações de colunas
from utils.config import APP_CONFIG, STREAMLIT_APP_URL # Importa configurações globais

# ===============================
# Configuração da página Streamlit
# ===============================
st.set_page_config(page_title=APP_CONFIG["titulo"], layout="wide")
st.title(f"🐾 {APP_CONFIG['titulo']} – Sistema PETDOR")

# ===============================
# Inicialização do Banco de Dados e Migrações
# ===============================
if "supabase_connected" not in st.session_state:
    st.session_state.supabase_connected = False
    sucesso_conexao, msg_conexao = testar_conexao()
    if sucesso_conexao:
        st.session_state.supabase_connected = True
        logger.info("Conexão com Supabase estabelecida com sucesso.")
        sucesso_migracao, msg_migracao = migrar_colunas_desativacao()
        if sucesso_migracao:
            logger.info(f"Migração de colunas de desativação: {msg_migracao}")
        else:
            logger.error(f"Falha na migração de colunas de desativação: {msg_migracao}")
            st.error(f"Erro crítico na migração do banco de dados: {msg_migracao}")
    else:
        logger.error(f"Falha na conexão com Supabase: {msg_conexao}")
        st.error(f"Erro crítico: Não foi possível conectar ao banco de dados. {msg_conexao}")
        st.stop()

# ===============================
# Inicializa session_state para o aplicativo
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Login"
if "user" not in st.session_state:
    st.session_state.user = None

# ===============================
# Lógica principal do aplicativo
# ===============================

# Verifica se há parâmetros de URL para confirmação de e-mail ou reset de senha
query_params = st.query_params
if "action" in query_params:
    action = query_params["action"]
    token = query_params.get("token")

    if action == "confirm_email" and token:
        st.subheader("Confirmação de E-mail")
        sucesso, usuario_id, email_usuario, mensagem = validar_token_confirmacao_email(token)
        if sucesso:
            # Atualiza o status de email_confirmado no banco de dados
            if usuario_id:
                sucesso_atualizacao = atualizar_email_confirmado(usuario_id, True) # Função de auth.user
                if sucesso_atualizacao:
                    st.success(mensagem)
                    st.session_state.page = "Login"
                else:
                    st.error("Erro ao atualizar status de confirmação no banco de dados.")
            else:
                st.error("ID de usuário não encontrado no token de confirmação.")
        else:
            st.error(mensagem)
    elif action == "reset_password" and token:
        st.subheader("Redefinir Senha")
        sucesso, email_usuario, mensagem = validar_token_reset_senha(token) # Retorna email_usuario e mensagem
        if sucesso and email_usuario:
            st.info(f"Redefinindo senha para: {email_usuario}")
            nova_senha = st.text_input("Nova Senha", type="password")
            confirmar_senha = st.text_input("Confirmar Nova Senha", type="password")
            if st.button("Redefinir Senha"):
                if nova_senha and nova_senha == confirmar_senha:
                    # Chama a função de redefinição de senha que usa o email
                    sucesso_reset, msg_reset = redefinir_senha_com_token(token, nova_senha) # De auth.password_reset
                    if sucesso_reset:
                        st.success(msg_reset)
                        st.session_state.page = "Login"
                    else:
                        st.error(msg_reset)
                else:
                    st.error("As senhas não coincidem ou estão vazias.")
        else:
            st.error(mensagem) # Mensagem de erro do validar_token_reset_senha

    # Limpa os query_params e força um rerun para evitar que a URL persista
    # e o Streamlit tente reprocessar o token em cada interação.
    st.query_params.clear()
    st.rerun()

# Se o usuário está logado, mostra o menu lateral e as páginas
if st.session_state.logged_in:
    st.sidebar.markdown("---")
    st.sidebar.write(f"Bem-vindo(a), {st.session_state.user.get('nome', 'Usuário')}!")

    app_pages = {
        "Avaliação de Dor": avaliacao_app_render,
        "Cadastro de Pet": cadastro_pet_app_render,
    }

    # Adiciona a página de administração apenas se o usuário for Admin
    if st.session_state.user.get("tipo") == "Admin": # Usa 'tipo' conforme definido em auth.user
        app_pages["Administração"] = admin_app_render

    # Define a página inicial padrão após o login (pode ser Avaliação de Dor)
    if st.session_state.page not in app_pages:
        st.session_state.page = "Avaliação de Dor"

    selected_app_page = st.sidebar.selectbox(
        "Navegar",
        list(app_pages.keys()),
        index=list(app_pages.keys()).index(st.session_state.page) if st.session_state.page in app_pages else 0
    )
    st.session_state.page = selected_app_page

    # Renderiza a página selecionada
    render_function = app_pages.get(selected_app_page)
    if render_function:
        render_function()
    else:
        st.error("Página não encontrada ou não implementada.")

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun() # Usar st.rerun()

else:
    # Se não está logado, mostra as opções de Login e Cadastro
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", key="btn_login"):
            st.session_state.page = "Login"
    with col2:
        if st.button("Cadastrar", key="btn_cadastro"):
            st.session_state.page = "Cadastro"

    # Renderiza a página de Login ou Cadastro
    if st.session_state.page == "Login":
        login_app_render()
    elif st.session_state.page == "Cadastro":
        cadastro_app_render()
    else:
        # Caso o usuário clique em "Cadastrar" e depois volte, o padrão é Login
        st.session_state.page = "Login"
        login_app_render()

# Lógica para solicitar reset de senha (botão no app principal)
if st.session_state.page == "Login" and st.button("Esqueceu sua senha?", key="btn_forgot_password"):
    email_reset = st.text_input("Digite seu e-mail para resetar a senha:")
    if st.button("Enviar link de reset"):
        if email_reset:
            sucesso, mensagem = solicitar_reset_senha(email_reset) # De auth.password_reset
            if sucesso:
                st.success(mensagem)
            else:
                st.error(mensagem)
        else:
            st.error("Por favor, digite um e-mail.")
