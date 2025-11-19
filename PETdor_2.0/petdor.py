import streamlit as st
from database.migration import migrar_banco_completo
from auth.user import (
    cadastrar_usuario,
    autenticar_usuario,
    buscar_usuario_por_id
)
from pages.cadastro_pet import app as cadastro_pet_app
from pages.avaliacao import app as avaliacao_app
# Importações corrigidas para corresponder aos nomes das funções em auth/password_reset.py
from auth.password_reset import solicitar_reset_senha, validar_token_reset, redefinir_senha

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
    st.subheader("Login")
    email = st.text_input("E-mail", key="login_email")
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Entrar", key="btn_login"):
        ok, msg, user_id = autenticar_usuario(email, senha)
        if ok:
            st.success(msg)
            st.session_state.user_id = user_id
            st.session_state.page = "avaliacao" # Redireciona para a página de avaliação
        else:
            st.error(msg)

    if "user_id" in st.session_state and st.session_state.page == "avaliacao":
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
    st.subheader("Criar Nova Conta")
    nome = st.text_input("Nome", key="criar_nome")
    email = st.text_input("E-mail", key="criar_email")
    senha = st.text_input("Senha", type="password", key="criar_senha")
    confirmar = st.text_input("Confirmar senha", type="password", key="criar_confirmar")
    if st.button("Criar", key="btn_criar_conta"):
        ok, msg = cadastrar_usuario(nome, email, senha, confirmar)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

# -------------------------------
# REDEFINIR SENHA
# -------------------------------
elif menu == "Redefinir Senha":
    st.subheader("Redefinir Senha")
    email_reset = st.text_input("Seu e-mail", key="reset_email")
    if st.button("Enviar link de redefinição", key="btn_enviar_token"):
        # A função solicitar_reset_senha envia o e-mail e retorna True/False
        ok = solicitar_reset_senha(email_reset)
        if ok:
            st.info("Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha.")
        else:
            st.error("Ocorreu um erro ao tentar enviar o e-mail. Tente novamente mais tarde.")

    st.markdown("---") # Separador visual
    st.write("Ou, se você já tem um token:")
    token_input = st.text_input("Token de redefinição", key="reset_token")
    nova_senha = st.text_input("Nova senha", type="password", key="reset_nova_senha")

    if st.button("Alterar senha", key="btn_alterar_senha"):
        if not token_input or not nova_senha:
            st.error("Preencha o token e a nova senha.")
        else:
            # 1. Validar o token e obter o ID do usuário
            token_valido_status, usuario_id = validar_token_reset(token_input)

            if token_valido_status and usuario_id:
                # 2. Redefinir a senha
                ok_redefinir = redefinir_senha(usuario_id, nova_senha, token_input)
                if ok_redefinir:
                    st.success("Senha alterada com sucesso! Você já pode fazer login.")
                else:
                    st.error("Erro ao redefinir a senha. Tente novamente.")
            else:
                st.error("Token inválido ou expirado.")
