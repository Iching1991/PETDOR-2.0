# PetDor2/pages/login.py
"""
Página de login do PETDor2.
Permite autenticar usuários e inicializar a sessão.
"""

import streamlit as st
import logging

# 🔧 Imports absolutos
from backend.auth.user import verificar_credenciais
from backend.auth.security import usuario_logado
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)

def render():
    """Renderiza a página de login."""
    st.header("🔐 Login")
    st.write("Acesse sua conta para continuar.")

    # Se o usuário já estiver logado, não mostra o formulário
    if usuario_logado(st.session_state):
        st.info("Você já está logado!")
        return

    with st.form("login_form"):
        email = st.text_input("E-mail", key="login_email_input").lower().strip()
        senha = st.text_input("Senha", type="password", key="login_senha_input")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            # Validação de e-mail
            if not email:
                st.error("❌ Por favor, digite seu e-mail.")
                return
            if not validar_email(email):
                st.error("❌ E-mail inválido.")
                return
            if not senha:
                st.error("❌ Por favor, digite sua senha.")
                return

            # Autenticação
            success, resultado = verificar_credenciais(email, senha)
            if success:
                user_data = resultado

                # Verifica se o e-mail está confirmado
                if not user_data.get("email_confirmado", False):
                    st.warning("⚠️ Seu e-mail ainda não foi confirmado. Verifique sua caixa de entrada.")
                    return

                # Armazena dados no session_state
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user_data.get("id")
                st.session_state["user_data"] = user_data
                st.session_state["user_email"] = user_data.get("email")
                st.session_state["user_name"] = user_data.get("nome")
                st.session_state["is_admin"] = user_data.get("tipo") == "Admin"

                st.success("✔ Login realizado com sucesso!")
                logger.info(f"Usuário {email} logado com sucesso. ID: {user_data.get('id')}")

                # Redireciona para página inicial padrão
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error(resultado)
                logger.warning(f"Falha no login para {email}: {resultado}")

    # Link para redefinir senha
    st.markdown("---")
    st.markdown("Esqueceu sua senha? Clique [aqui](#) para redefinir.")
