# PetDor2/pages/home.py
import streamlit as st
import logging

# ===============================
# Configuração de logging
# ===============================
logger = logging.getLogger(__name__)

# ===============================
# Importações absolutas a partir da raiz do projeto
# ===============================
from auth.security import usuario_logado, logout # Importa as funções de sessão

def render():
    """
    Renderiza a página inicial (dashboard) após o login.
    """
    st.title("🏠 Página Inicial")

    # Verifica se o usuário está logado usando a função centralizada
    if not usuario_logado(st.session_state):
        st.warning("Você precisa estar logado para acessar esta página.")
        # O streamlit_app.py principal irá redirecionar para a página de login
        # Não precisamos de st.session_state.page = "login" ou st.rerun() aqui,
        # pois o app principal já cuida disso ao verificar usuario_logado().
        return

    # Acessa os dados do usuário a partir de st.session_state.user_data
    user_data = st.session_state.get("user_data")

    if user_data:
        st.success(f"Bem-vindo(a), {user_data.get('nome', 'usuário')}!")
        st.write("Aqui ficará o dashboard, estatísticas, atalhos e funcionalidades principais do PETDOR.")
        st.write("Use o menu lateral para navegar entre as funcionalidades.")

        # Exemplo de informações do usuário (opcional)
        st.subheader("Suas informações:")
        st.write(f"**E-mail:** {user_data.get('email')}")
        st.write(f"**Tipo de Usuário:** {user_data.get('tipo')}")
        st.write(f"**País:** {user_data.get('pais')}")

        # Botão de sair, usando a função de logout centralizada
        if st.button("Sair da Conta", key="btn_logout_home"):
            logout(st.session_state)
            st.rerun() # Força a reexecução para limpar a interface e mostrar o login
    else:
        # Caso o usuario_logado retorne True, mas user_data esteja vazio (situação improvável)
        st.error("Erro: Dados do usuário não encontrados na sessão. Por favor, faça login novamente.")
        logout(st.session_state)
        st.rerun()
