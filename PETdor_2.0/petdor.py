# PetDor/petdor.py
import streamlit as st
from database.migration import migrar_banco_completo
from auth.user import (
    cadastrar_usuario,
    autenticar_usuario,
    buscar_usuario_por_id
)
from pages.cadastro_pet import app as cadastro_pet_app
from pages.avaliacao import app as avaliacao_app
from auth.password_reset import reset_password_request, redefinir_senha

# 🔧 Inicializa banco
migrar_banco_completo()

# Configuração da página
st.set_page_config(page_title="PETDOR – Avaliação de Dor", layout="centered")
st.title("🐾 PETDOR – Sistema PETDOR")

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Login", "Criar Conta", "Redefinir Senha"])

# -------------------------------
# LOGIN
# -------------------------------
if menu == "Login":
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        ok, msg, user_id = autenticar_usuario(email, senha)
        if ok:
            st.success(msg)
            st.session_state.user_id = user_id
        else:
            st.error(msg)

    if "user_id" in st.session_state:
        user_id = st.session_state.user_id
        st.subheader("Cadastro e Avaliações")

        # Cadastro de Pets
        cadastro_pet_app(user_id)

        # Avaliações
        avaliacao_app(user_id)

# -------------------------------
# CRIAR CONTA
# -------------------------------
elif menu == "Criar Conta":
    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    if st.button("Criar"):
        ok, msg = cadastrar_usuario(nome, email, senha, confirmar)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

# -------------------------------
# REDEFINIR SENHA
# -------------------------------
elif menu == "Redefinir Senha":
    email = st.text_input("Seu e-mail")
    if st.button("Enviar token"):
        token = reset_password_request(email)
        if token:
            st.info(f"Token gerado: {token}\n\nCopie e cole abaixo.")
        else:
            st.error("E-mail não encontrado.")

    token = st.text_input("Token")
    nova = st.text_input("Nova senha", type="password")
    if st.button("Alterar senha"):
        if reset_password(token, nova):
            st.success("Senha alterada com sucesso!")
        else:
            st.error("Token inválido ou expirado.")

