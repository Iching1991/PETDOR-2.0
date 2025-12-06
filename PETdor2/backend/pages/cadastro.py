"""
Página de cadastro de usuários - PETDor2
Permite criar uma nova conta no sistema.
"""

import streamlit as st

# 🔧 Import absoluto do backend
from backend.auth.user import cadastrar_usuario

def render():
    """Renderiza a página de cadastro de usuário."""
    st.title("📝 Criar Conta")
    st.markdown("Preencha os dados abaixo para criar sua conta no PETDor.")

    # -----------------------------
    # Campos do formulário
    # -----------------------------
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    pais = st.selectbox("País", ["Brasil", "Portugal", "EUA", "Outro"])
    tipo = st.selectbox("Tipo de conta", ["Tutor", "Veterinário", "Clínica"])

    # -----------------------------
    # Botão de cadastro
    # -----------------------------
    if st.button("Criar Conta"):
        # Validação simples
        if senha != confirmar:
            st.error("❌ As senhas não coincidem.")
            return

        if len(senha) < 6:
            st.error("❌ A senha deve ter pelo menos 6 caracteres.")
            return

        ok, msg = cadastrar_usuario(nome, email, senha, tipo, pais)

        if ok:
            st.success("✅ " + msg)
            st.info("📧 Verifique seu e-mail para confirmar sua conta.")
            st.session_state.pagina = "login"
            st.rerun()
        else:
            st.error("❌ " + msg)

    # -----------------------------
    # Observações
    # -----------------------------
    st.markdown(
        """
        ---
        **Observações:**  
        - Contas *Veterinário* e *Clínica* poderão adicionar CRMV / CNPJ posteriormente.  
        - O país é apenas informativo por enquanto.  
        """
    )

__all__ = ["render"]
