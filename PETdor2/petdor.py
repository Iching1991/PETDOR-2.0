# PETdor_2_0/petdor.py
import streamlit as st
import sys
import os

# ============================================================
# 🔧 CORREÇÃO DOS IMPORTS (ABSOLUTOS)
# ============================================================

# Caminho da pasta PETdor_2_0
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Garante que PETdor_2_0 está no sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Agora todos os imports são feitos a partir de PETdor_2_0.<módulo>
from PETdor_2_0.database.migration import migrar_banco_completo

from PETdor_2_0.auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
)

from PETdor_2_0.auth.password_reset import (
    solicitar_reset_senha,
    validar_token_reset,
    redefinir_senha_com_token,
)

from PETdor_2_0.pages.cadastro_pet import app as cadastro_pet_app
from PETdor_2_0.pages.avaliacao import app as avaliacao_app


# ============================================================
# 🔧 Inicializa banco de dados
# ============================================================
migrar_banco_completo()


# ============================================================
# 🎨 Configuração da página
# ============================================================
st.set_page_config(page_title="PETDOR – Avaliação de Dor", layout="centered")
st.title("🐾 PETDOR – Sistema PETDOR")

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Login", "Criar Conta", "Redefinir Senha"])


# ============================================================
# 🔐 LOGIN
# ============================================================
if menu == "Login":
    st.subheader("Login")
    email = st.text_input("E-mail", key="login_email").lower()
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar", key="btn_login"):
        ok, msg_ou_usuario = verificar_credenciais(email, senha)

        if ok:
            st.success("Login bem-sucedido!")
            st.session_state.user_id = msg_ou_usuario['id']
            st.session_state.user_email = msg_ou_usuario['email']
            st.session_state.user_name = msg_ou_usuario['nome']
            st.session_state.page = "avaliacao"
            st.rerun()
        else:
            st.error(msg_ou_usuario)

    # Após login
    if "user_id" in st.session_state and st.session_state.page == "avaliacao":
        user_id = st.session_state.user_id

        st.subheader(f"Bem-vindo(a), {st.session_state.user_name}!")

        sub_menu = st.sidebar.selectbox("Opções", ["Meus Pets e Avaliações", "Sair"])

        if sub_menu == "Meus Pets e Avaliações":
            cadastro_pet_app(user_id)
            avaliacao_app(user_id)

        elif sub_menu == "Sair":
            st.session_state.clear()
            st.rerun()


# ============================================================
# 🧾 CRIAR CONTA
# ============================================================
elif menu == "Criar Conta":
    st.subheader("Criar Nova Conta")

    with st.form("form_cadastro"):
        nome = st.text_input("Nome Completo").title()
        email = st.text_input("E-mail").lower()
        senha = st.text_input("Senha", type="password")
        senha2 = st.text_input("Confirmar Senha", type="password")
        tipo_usuario = st.selectbox("Tipo de Usuário", ["Tutor", "Veterinário", "Clínica"])
        pais = st.text_input("País", value="Brasil")

        enviar = st.form_submit_button("Cadastrar")

        if enviar:
            if not nome or not email or not senha or not senha2:
                st.error("Por favor, preencha todos os campos.")
            elif senha != senha2:
                st.error("As senhas não coincidem.")
            elif len(senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                ok, msg = cadastrar_usuario(nome, email, senha, tipo_usuario, pais)
                if ok:
                    st.success(msg)
                    st.info("Agora você pode fazer login.")
                else:
                    st.error(msg)


# ============================================================
# 🔄 REDEFINIR SENHA
# ============================================================
elif menu == "Redefinir Senha":
    st.subheader("Redefinir Senha")

    # Verifica se chegou um token na URL
    query_params = st.query_params
    token_url = query_params.get("token")

    # -----------------------------------------
    # 🔗 Fluxo via link de e-mail
    # -----------------------------------------
    if token_url:
        st.info("Você está redefinindo sua senha através de um link enviado por e-mail.")

        token_valido, msg_validacao, email_do_usuario = validar_token_reset(token_url)

        if token_valido and email_do_usuario:
            st.success(msg_validacao)
            st.write(f"Redefinindo senha para: **{email_do_usuario}**")

            nova = st.text_input("Nova senha", type="password")
            nova2 = st.text_input("Confirmar nova senha", type="password")

            if st.button("Alterar senha"):
                if not nova or not nova2:
                    st.error("Preencha a nova senha e a confirmação.")
                elif nova != nova2:
                    st.error("As senhas não coincidem.")
                elif len(nova) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                else:
                    ok, msg = redefinir_senha_com_token(token_url, nova)
                    if ok:
                        st.success(msg)
                        st.info("Você pode fazer login agora.")
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.error(msg_validacao)
            st.info("Solicite um novo link de redefinição.")
            st.query_params.clear()
            st.rerun()

    # -----------------------------------------
    # 📨 Fluxo normal (solicitar link)
    # -----------------------------------------
    else:
        email_reset = st.text_input("Seu e-mail").lower()

        if st.button("Enviar link de redefinição"):
            ok, msg = solicitar_reset_senha(email_reset)
            if ok:
                st.info(msg)
            else:
                st.error(msg)

        st.markdown("---")

        st.write("Ou redefina manualmente com um token:")

        token_manual = st.text_input("Token")
        nova = st.text_input("Nova senha", type="password")
        nova2 = st.text_input("Confirmar nova senha", type="password")

        if st.button("Alterar senha manualmente"):
            if not token_manual or not nova or not nova2:
                st.error("Preencha todos os campos.")
            elif nova != nova2:
                st.error("As senhas não coincidem.")
            else:
                valido, msg_validacao, email_usuario = validar_token_reset(token_manual)

                if valido and email_usuario:
                    ok, msg = redefinir_senha_com_token(token_manual, nova)
                    if ok:
                        st.success(msg)
                        st.info("Você pode fazer login agora.")
                    else:
                        st.error(msg)
                else:
                    st.error(msg_validacao)
