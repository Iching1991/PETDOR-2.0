# PETdor2/backend/pages/login.py
import streamlit as st
from ..auth.user import verificar_credenciais
from ..utils.validators import validar_email
from ..utils.tokens import gerar_token_sessao  # se você quiser gerar token extra

def render():
    st.header("🔐 Login")
    st.write("Acesse sua conta para continuar.")

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        # 1️⃣ Validação de e-mail
        if not validar_email(email):
            st.error("❌ Email inválido.")
            return

        # 2️⃣ Autenticação via Supabase
        success, usuario = verificar_credenciais(email, senha)

        if success:
            # 3️⃣ Cria token de sessão opcional
            token = gerar_token_sessao(usuario.get("id")) if "id" in usuario else None

            # 4️⃣ Armazena session_state
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = usuario.get("id")
            st.session_state["user_type"] = usuario.get("tipo", "tutor")
            st.session_state["token"] = token

            st.success("✔ Login realizado com sucesso!")
            st.experimental_rerun()  # atualiza a página
        else:
            st.error(usuario.get("erro", "❌ Email ou senha incorretos."))
