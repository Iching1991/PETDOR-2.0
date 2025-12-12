# PetDor2/pages/home.py
"""
Página inicial (dashboard) do PETDor2.
Exibe informações básicas do usuário e links rápidos para funcionalidades.
"""

import streamlit as st
import logging

# 🔧 Imports absolutos
from backend.auth.security import usuario_logado, logout  # Funções de sessão centralizadas

logger = logging.getLogger(__name__)

def render():
    """
    Renderiza a página inicial após o login.
    """
    st.title("🏠 Página Inicial")

    # Verifica se o usuário está logado
    if not usuario_logado(st.session_state):
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    # Dados do usuário
    user_data = st.session_state.get("user_data")
    if not user_data:
        st.error("❌ Dados do usuário não encontrados na sessão. Por favor, faça login novamente.")
        logout(st.session_state)
        st.rerun()

    # Mensagem de boas-vindas
    st.success(f"Bem-vindo(a), {user_data.get('nome', 'usuário')}!")
    st.write("Aqui ficará o dashboard, estatísticas, atalhos e funcionalidades principais do PETDOR.")
    st.write("Use o menu lateral para navegar entre as funcionalidades.")

    # Informações do usuário
    st.subheader("Suas informações:")
    st.write(f"**E-mail:** {user_data.get('email', 'Não informado')}")
    st.write(f"**Tipo de Usuário:** {user_data.get('tipo', 'Não informado')}")
    st.write(f"**País:** {user_data.get('pais', 'Não informado')}")

    # Botão de logout
    if st.button("🚪 Sair da Conta", key="btn_logout_home"):
        logout(st.session_state)
        st.success("✅ Você saiu da conta com sucesso.")
        st.rerun()

__all__ = ["render"]
