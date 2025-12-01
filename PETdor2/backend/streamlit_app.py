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
# Ajuste do sys.path para imports absolutos
# ===============================
# Adiciona o diretório raiz do projeto (PetDor2/) ao sys.path
# Isso permite importar módulos como 'auth.user' ou 'pages.login'
# sem problemas de "top-level package".
# Assumimos que streamlit_app.py está na raiz do projeto PetDor2/
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ===============================
# Importações absolutas a partir da raiz do projeto
# ===============================
# Módulos de Autenticação e Usuário
from auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
    buscar_usuario_por_id,
    marcar_email_como_confirmado, # Nova função para marcar e-mail confirmado
    atualizar_usuario, # Para atualizar dados do usuário se necessário
)
from auth.security import (
    gerar_token_reset_senha, validar_token_reset_senha,
    gerar_token_confirmacao_email, validar_token_confirmacao_email,
    hash_password, verify_password,
    usuario_logado, logout # Funções de sessão
)
from auth.password_reset import solicitar_reset_senha, redefinir_senha_com_token
from auth.email_confirmation import confirmar_email_com_token # Função principal de confirmação

# Módulos de Páginas (assumindo que as páginas estão em PetDor2/pages/)
from pages.login import render as login_app_render
from pages.cadastro import render as cadastro_app_render
from pages.cadastro_pet import render as cadastro_pet_app_render
from pages.avaliacao import render as avaliacao_app_render
from pages.admin import render as admin_app_render # Página de administração

# Módulos de Banco de Dados e Configurações
from database.supabase_client import testar_conexao # Para testar a conexão com Supabase
# from database.migrations import migrar_colunas_desativacao # REMOVIDO: Migrações são para SQLite ou feitas no Supabase UI
from utils.config import APP_CONFIG, STREAMLIT_APP_URL # Importa configurações globais

# ===============================
# Configuração da página Streamlit
# ===============================
st.set_page_config(page_title=APP_CONFIG["titulo"], layout="wide")
st.title(f"🐾 {APP_CONFIG['titulo']} – Sistema PETDOR")

# ===============================
# Inicialização do Banco de Dados (Supabase)
# ===============================
if "supabase_connected" not in st.session_state:
    st.session_state.supabase_connected = False
    try:
        sucesso_conexao = testar_conexao() # testar_conexao retorna apenas bool
        if sucesso_conexao:
            st.session_state.supabase_connected = True
            logger.info("✅ Conexão com Supabase estabelecida com sucesso.")
            # Não há migrações de colunas aqui, pois é Supabase.
            # Se precisar de migrações, elas seriam feitas manualmente no Supabase ou via scripts externos.
        else:
            logger.error("❌ Falha na conexão com Supabase.")
            st.error("❌ Erro crítico: Não foi possível conectar ao banco de dados. Verifique as variáveis de ambiente.")
            st.stop()
    except RuntimeError as e:
        logger.error(f"❌ Erro de configuração do Supabase: {e}")
        st.error(f"❌ Erro crítico de configuração do Supabase: {e}")
        st.stop()
    except Exception as e:
        logger.error(f"❌ Erro inesperado na inicialização do Supabase: {e}", exc_info=True)
        st.error(f"❌ Erro inesperado na inicialização do Supabase: {e}")
        st.stop()

# ===============================
# Inicializa session_state para o aplicativo
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Login" # Página padrão
if "user_data" not in st.session_state: # Armazena todos os dados do usuário logado
    st.session_state.user_data = None

# ===============================
# Lógica principal do aplicativo
# ===============================

# Verifica se há parâmetros de URL para ações específicas (confirmação/reset)
query_params = st.query_params

if "action" in query_params and "token" in query_params:
    action = query_params["action"]
    token = query_params["token"]

    if action == "confirm_email":
        st.subheader("Confirmação de E-mail")
        sucesso, mensagem = confirmar_email_com_token(token) # Chama a função principal de confirmação
        if sucesso:
            st.success(mensagem)
            st.session_state.page = "Login" # Redireciona para login após sucesso
        else:
            st.error(mensagem)
        # Limpa os query_params e força um rerun para evitar reprocessamento
        st.query_params.clear()
        st.rerun()

    elif action == "reset_password":
        st.subheader("Redefinir Senha")
        # Validar o token de reset para obter o email do usuário
        valido, email_do_token, mensagem_validacao = validar_token_reset_senha(token)

        if valido and email_do_token:
            st.info(f"Redefinindo senha para: {email_do_token}")
            nova_senha = st.text_input("Nova Senha", type="password", key="reset_nova_senha")
            confirmar_senha = st.text_input("Confirmar Nova Senha", type="password", key="reset_confirmar_senha")

            if st.button("Redefinir Senha", key="btn_redefinir_senha_form"):
                if nova_senha and nova_senha == confirmar_senha:
                    if len(nova_senha) < 8:
                        st.error("A nova senha deve ter pelo menos 8 caracteres.")
                    else:
                        sucesso_reset, msg_reset = redefinir_senha_com_token(token, nova_senha)
                        if sucesso_reset:
                            st.success(msg_reset)
                            st.session_state.page = "Login" # Redireciona para login
                        else:
                            st.error(msg_reset)
                else:
                    st.error("As senhas não coincidem ou estão vazias.")
        else:
            st.error(mensagem_validacao) # Mensagem de erro do validar_token_reset_senha

        # Limpa os query_params e força um rerun para evitar reprocessamento
        st.query_params.clear()
        st.rerun()

# Se o usuário está logado, mostra o menu lateral e as páginas
if st.session_state.logged_in and st.session_state.user_data:
    st.sidebar.markdown("---")
    st.sidebar.write(f"Bem-vindo(a), {st.session_state.user_data.get('nome', 'Usuário')}!")

    app_pages = {
        "Avaliação de Dor": avaliacao_app_render,
        "Cadastro de Pet": cadastro_pet_app_render,
    }

    # Adiciona a página de administração apenas se o usuário for Admin
    if st.session_state.user_data.get("tipo") == "Admin":
        app_pages["Administração"] = admin_app_render

    # Define a página inicial padrão após o login
    if st.session_state.page not in app_pages:
        st.session_state.page = "Avaliação de Dor" # Página padrão após login

    selected_app_page = st.sidebar.selectbox(
        "Navegar",
        list(app_pages.keys()),
        index=list(app_pages.keys()).index(st.session_state.page) if st.session_state.page in app_pages else 0,
        key="sidebar_navigation"
    )
    st.session_state.page = selected_app_page

    # Renderiza a página selecionada
    render_function = app_pages.get(selected_app_page)
    if render_function:
        # Passa user_data para as páginas que precisam
        render_function(user_data=st.session_state.user_data)
    else:
        st.error("Página não encontrada ou não implementada.")

    if st.sidebar.button("Sair", key="btn_logout_sidebar"):
        logout(st.session_state) # Usa a função de logout de auth.security
        st.rerun()

else:
    # Se não está logado, mostra as opções de Login e Cadastro
    st.sidebar.markdown("---")
    st.sidebar.write("Acesso:")

    menu_nao_logado = st.sidebar.radio(
        "Selecione uma opção:",
        ["Login", "Criar Conta", "Redefinir Senha"],
        index=0 if st.session_state.page == "Login" else (1 if st.session_state.page == "Cadastro" else 2),
        key="menu_nao_logado"
    )
    st.session_state.page = menu_nao_logado

    if st.session_state.page == "Login":
        login_app_render()
    elif st.session_state.page == "Criar Conta":
        cadastro_app_render()
    elif st.session_state.page == "Redefinir Senha":
        st.subheader("Redefinir Senha")
        email_reset = st.text_input("Digite seu e-mail para resetar a senha:", key="email_reset_input")
        if st.button("Enviar link de reset", key="btn_enviar_reset"):
            if email_reset:
                sucesso, mensagem = solicitar_reset_senha(email_reset)
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)
            else:
                st.error("Por favor, digite um e-mail.")

