# PETdor2/streamlit_app.py

import sys
import os
import streamlit as st

# --- Corrige importações para Streamlit Cloud ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim correção ---

# ===========================
# Importações do banco e auth
# ===========================
from database.migration import migrar_banco_completo
from auth.user import cadastrar_usuario, verificar_credenciais, confirmar_email
from auth.password_reset import solicitar_reset_senha, validar_token_reset, redefinir_senha_com_token

# ===========================
# Importações das páginas
# ===========================
from pages.cadastro_pet import render as cadastro_pet_app
from pages.avaliacao import render as avaliacao_app
from pages.home import render as home_app
from pages.perfil import render as perfil_app

# ===========================
# Inicializa banco
# ===========================
migrar_banco_completo()

# ===========================
# Configurações da página
# ===========================
st.set_page_config(page_title="PETDOR – Sistema PETDOR", layout="centered")
st.title("🐾 PETDOR – Sistema PETDOR")

# ===========================
# Lógica de URL parameters (confirmar e-mail / reset password)
# ===========================
query_params = st.query_params
if "token" in query_params and "action" in query_params:
    token = query_params["token"]
    action = query_params["action"][0] if isinstance(query_params["action"], list) else query_params["action"]

    if action == "confirm_email":
        st.subheader("Confirmação de E-mail")
        ok, msg = confirmar_email(token)
        st.success(msg) if ok else st.error(msg)
        st.experimental_set_query_params()  # limpa query params
        st.stop()

    elif action == "reset_password":
        st.subheader("Redefinir Senha")
        st.info("Insira sua nova senha.")
        nova_senha = st.text_input("Nova Senha", type="password", key="reset_nova_senha_url")
        confirmar_nova_senha = st.text_input("Confirmar Nova Senha", type="password", key="reset_confirmar_nova_senha_url")
        if st.button("Redefinir Senha", key="btn_redefinir_url"):
            if not nova_senha or not confirmar_nova_senha:
                st.error("Preencha ambos os campos de senha.")
            elif nova_senha != confirmar_nova_senha:
                st.error("As senhas não coincidem.")
            else:
                ok, msg = redefinir_senha_com_token(token, nova_senha)
                st.success(msg) if ok else st.error(msg)
                st.experimental_set_query_params()
                st.stop()
        st.stop()

# ===========================
# Menu lateral principal (login / criar conta / reset)
# ===========================
menu = st.sidebar.selectbox("Menu", ["Login", "Criar Conta", "Redefinir Senha"])

# ---------------------------
# LOGIN
# ---------------------------
if menu == "Login":
    st.subheader("Login")
    email = st.text_input("E-mail", key="login_email").lower()
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Entrar", key="btn_login"):
        ok, result = verificar_credenciais(email, senha)
        if ok:
            st.success("Login bem-sucedido!")
            st.session_state.update({
                "usuario": result,
                "logged_in": True,
                "page": "Home"
            })
            st.rerun()
        else:
            st.error(result)

# ---------------------------
# CRIAR CONTA
# ---------------------------
elif menu == "Criar Conta":
    st.subheader("Criar Nova Conta")
    with st.form("cadastro_form"):
        nome = st.text_input("Nome Completo").title()
        email = st.text_input("E-mail").lower()
        senha = st.text_input("Senha", type="password")
        confirmar_senha = st.text_input("Confirmar Senha", type="password")
        tipo_usuario = st.selectbox("Tipo de Usuário", ["Tutor", "Veterinário", "Clínica"])
        pais = st.text_input("País", value="Brasil").title()
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            if not nome or not email or not senha or not confirmar_senha:
                st.error("Preencha todos os campos.")
            elif senha != confirmar_senha:
                st.error("As senhas não coincidem.")
            else:
                ok, msg = cadastrar_usuario(nome, email, senha, tipo_usuario, pais)
                st.success(msg) if ok else st.error(msg)
                if ok:
                    st.info("Confirme seu e-mail antes de fazer login.")

# ---------------------------
# REDEFINIR SENHA
# ---------------------------
elif menu == "Redefinir Senha":
    st.subheader("Redefinir Senha")
    email_reset = st.text_input("Seu e-mail").lower()
    if st.button("Enviar link de redefinição"):
        ok, msg = solicitar_reset_senha(email_reset)
        st.info(msg) if ok else st.error(msg)

    st.markdown("---")
    st.write("Ou, se você já tem um token e não está usando o link do e-mail:")
    token_input = st.text_input("Token")
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar_nova_senha_manual = st.text_input("Confirmar nova senha", type="password")
    if st.button("Alterar senha manualmente"):
        if not token_input or not nova_senha or not confirmar_nova_senha_manual:
            st.error("Preencha o token e a nova senha.")
        elif nova_senha != confirmar_nova_senha_manual:
            st.error("As senhas não coincidem.")
        else:
            valido, msg_val, email_usuario = validar_token_reset(token_input)
            if valido and email_usuario:
                ok, msg = redefinir_senha_com_token(token_input, nova_senha)
                st.success(msg) if ok else st.error(msg)
            else:
                st.error(msg_val)

# ===========================
# Páginas do sistema (após login)
# ===========================
if st.session_state.get("logged_in"):
    st.sidebar.markdown("---")
    st.sidebar.title("Navegação")

    paginas = {
        "Home": home_app,
        "Cadastro de Pet": cadastro_pet_app,
        "Avaliação de Dor": avaliacao_app,
        "Perfil": perfil_app
    }

    selected_page = st.sidebar.selectbox(
        "Selecionar Página",
        list(paginas.keys()),
        index=list(paginas.keys()).index(st.session_state.get("page", "Home"))
    )

    st.session_state["page"] = selected_page
    paginas[selected_page]()

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()
