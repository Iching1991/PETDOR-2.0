import streamlit as st
from utils.validators import validar_email
from utils.tokens import gerar_token_sessao
from database.connection import conectar_db


def autenticar_usuario(email, senha):
    """Verifica se o usuário existe e se a senha está correta."""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, senha FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None  # Usuário não encontrado

    user_id, senha_correta = row

    if senha != senha_correta:
        return None

    return user_id


def render():
    st.title("🔐 Login")
    st.write("Acesse sua conta para continuar.")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not validar_email(email):
            st.error("❌ Email inválido.")
            return

        user_id = autenticar_usuario(email, senha)

        if user_id:
            token = gerar_token_sessao(user_id)
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.session_state["token"] = token

            st.success("✔ Login realizado com sucesso!")
            st.switch_page("pages/home.py")
        else:
            st.error("❌ Email ou senha incorretos.")
