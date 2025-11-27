# PETdor2/pages/confirmar_email.py 
"""
Página de confirmação de e-mail após registro.
O usuário recebe um link com token e confirma seu e-mail aqui.
"""
import streamlit as st
import logging
from auth.email_confirmation import validar_token_confirmacao, confirmar_email

logger = logging.getLogger(__name__)

def get_query_params():
    """Lê parâmetros da URL de forma compatível com todas as versões do Streamlit."""
    try:
        # Streamlit 1.30+
        return st.query_params
    except Exception:
        # Versões antigas (experimental)
        return st.experimental_get_query_params()

def render():
    """Renderiza a página de confirmação de e-mail."""
    st.header("📧 Confirmar E-mail")

    # Obtém token da URL (compatível com todas as versões)
    query_params = get_query_params()
    token = query_params.get("token", [None])[0]

    if not token:
        st.warning("⚠️ Token de confirmação não fornecido.")
        st.info("Verifique o link enviado para seu e-mail.")
        return

    # Valida token
    token_valido, usuario_id = validar_token_confirmacao(token)

    if not token_valido:
        st.error("❌ Token inválido ou expirado.")
        st.info("Solicite um novo link de confirmação.")
        return

    # Token válido - confirma e-mail
    sucesso, mensagem = confirmar_email(usuario_id)

    if sucesso:
        st.success("✅ E-mail confirmado com sucesso!")
        st.info("Você já pode fazer login na plataforma.")

        if st.button("🔐 Ir para Login"):
            st.session_state.pagina = "login"
            st.rerun()
    else:
        st.error(f"❌ Erro ao confirmar e-mail: {mensagem}")

__all__ = ["render"]
