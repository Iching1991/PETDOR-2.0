# PETdor2/streamlit_app.py
import streamlit as st
import sys
import os

# --- INÍCIO DA CORREÇÃO DE IMPORTAÇÃO ---
# Adiciona o diretório atual (PETdor2) ao sys.path para resolver importações absolutas
# Isso permite que módulos como 'auth', 'utils' e 'database' sejam importados diretamente
# como 'auth.user' ou 'utils.email_sender' ou 'database.connection' de qualquer lugar dentro do projeto.
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# current_script_dir agora é '/mount/src/petdor2/PETdor2' (se o app está em /mount/src/petdor2/PETdor2/streamlit_app.py)
# Se o seu projeto está estruturado como /mount/src/petdor2/PETdor2/ e dentro de PETdor2/ estão auth, database, etc.
# Então o diretório a ser adicionado é current_script_dir
if current_script_dir not in sys.path:
    sys.path.insert(0, current_script_dir)
# --- FIM DA CORREÇÃO DE IMPORTAÇÃO ---

# Agora as importações devem funcionar
from database.migration import migrar_banco_completo 
# Importações corrigidas para corresponder aos nomes das funções em auth/user.py
from auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
    # Se você tiver uma função buscar_usuario_por_id, mantenha-a ou ajuste conforme necessário
)
# Importações corrigidas para corresponder aos nomes das funções em auth/password_reset.py
from auth.password_reset import solicitar_reset_senha, validar_token_reset, redefinir_senha_com_token

from pages.cadastro_pet import app as cadastro_pet_app
from pages.avaliacao import app as avaliacao_app

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
    email = st.text_input("E-mail", key="login_email").lower() # Email em minúsculas
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Entrar", key="btn_login"):
        ok, msg_ou_usuario = verificar_credenciais(email, senha)
        if ok:
            st.success("Login bem-sucedido!")
            st.session_state.user_id = msg_ou_usuario['id'] # Pega o ID do usuário retornado
            st.session_state.user_email = msg_ou_usuario['email']
            st.session_state.user_name = msg_ou_usuario['nome']
            st.session_state.user_type = msg_ou_usuario['tipo_usuario']
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error(msg_ou_usuario)

# -------------------------------
# CRIAR CONTA
# -------------------------------
elif menu == "Criar Conta":
    st.subheader("Criar Nova Conta")
    with st.form("cadastro_form"):
        novo_nome = st.text_input("Nome Completo").title() # Nome com primeira letra maiúscula
        novo_email = st.text_input("E-mail").lower() # Email em minúsculas
        nova_senha = st.text_input("Senha", type="password")
        confirmar_senha = st.text_input("Confirmar Senha", type="password")
        tipo_usuario = st.selectbox("Tipo de Usuário", ["Tutor", "Veterinário", "Clínica"])
        pais = st.text_input("País", value="Brasil") # Valor padrão "Brasil"

        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            if nova_senha != confirmar_senha:
                st.error("As senhas não coincidem.")
            else:
                ok, msg = cadastrar_usuario(novo_nome, novo_email, nova_senha, tipo_usuario, pais)
                if ok:
                    st.success(msg)
                    st.info("Verifique seu e-mail para confirmar a conta.")
                else:
                    st.error(msg)

# -------------------------------
# REDEFINIR SENHA
# -------------------------------
elif menu == "Redefinir Senha":
    st.subheader("Redefinir Senha")

    # Verifica se há um token na URL (vindo do e-mail)
    query_params = st.query_params
    token_url = query_params.get("token")

    if token_url:
        st.info("Você está redefinindo sua senha através de um link de e-mail.")
        st.write(f"Token recebido: `{token_url}`")

        # Formulário para nova senha
        nova_senha_url = st.text_input("Nova senha", type="password", key="reset_nova_senha_url")
        confirmar_nova_senha_url = st.text_input("Confirmar nova senha", type="password", key="reset_confirmar_nova_senha_url")
        if st.button("Redefinir Senha", key="btn_redefinir_url"):
            if not nova_senha_url or not confirmar_nova_senha_url:
                st.error("Preencha a nova senha e a confirmação.")
            elif nova_senha_url != confirmar_nova_senha_url:
                st.error("As senhas não coincidem.")
            else:
                # 1. Validar o token e obter o e-mail do usuário
                token_valido_status, msg_validacao, email_usuario_reset = validar_token_reset(token_url)
                if token_valido_status and email_usuario_reset:
                    # 2. Redefinir a senha
                    ok_redefinir, msg_redefinir = redefinir_senha_com_token(token_url, nova_senha_url)
                    if ok_redefinir:
                        st.success(msg_redefinir)
                        st.info("Você pode fazer login agora.")
                        # Limpa os query params para evitar reuso do token
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.error(msg_redefinir)
                else:
                    st.error(msg_validacao)
                    st.info("Por favor, solicite um novo link de redefinição de senha.")
                    # Limpa os query params para evitar reuso do token inválido
                    st.query_params.clear()
                    st.rerun()
    else: # Fluxo normal de solicitação de reset
        email_reset = st.text_input("Seu e-mail", key="reset_email").lower() # Email em minúsculas
        if st.button("Enviar link de redefinição", key="btn_enviar_token"):
            ok, msg = solicitar_reset_senha(email_reset) # A função agora retorna (bool, str)
            if ok:
                st.info(msg)
            else:
                st.error(msg)
        st.markdown("---") # Separador visual
        st.write("Ou, se você já tem um token e não está usando o link do e-mail:")
        token_input = st.text_input("Token de redefinição", key="reset_token_manual")
        nova_senha = st.text_input("Nova senha", type="password", key="reset_nova_senha_manual")
        confirmar_nova_senha_manual = st.text_input("Confirmar nova senha", type="password", key="reset_confirmar_nova_senha_manual")
        if st.button("Alterar senha manualmente", key="btn_alterar_senha_manual"):
            if not token_input or not nova_senha or not confirmar_nova_senha_manual:
                st.error("Preencha o token e a nova senha (e a confirmação).")
            elif nova_senha != confirmar_nova_senha_manual:
                st.error("As senhas não coincidem.")
            else:
                # 1. Validar o token e obter o e-mail do usuário
                token_valido_status, msg_validacao, email_usuario_reset = validar_token_reset(token_input)
                if token_valido_status and email_usuario_reset:
                    # 2. Redefinir a senha
                    ok_redefinir, msg_redefinir = redefinir_senha_com_token(token_input, nova_senha)
                    if ok_redefinir:
                        st.success(msg_redefinir)
                        st.info("Você pode fazer login agora.")
                    else:
                        st.error(msg_redefinir)
                else:
                    st.error(msg_validacao) # Exibe a mensagem de erro da validação do token
