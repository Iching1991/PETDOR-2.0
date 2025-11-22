# PETdor_2_0/petdor.py
import streamlit as st
import sys
import os

# Adiciona o diretório pai (PETdor_2_0) ao sys.path para resolver importações
# Isso permite que módulos como 'auth' e 'utils' sejam importados diretamente
# como 'auth.user' ou 'utils.email_sender' de qualquer lugar dentro do projeto.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # Sobe um nível para PETdor_2_0
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
            st.session_state.page = "avaliacao" # Redireciona para a página de avaliação
            st.rerun() # Força o rerun para mudar a página
        else:
            st.error(msg_ou_usuario) # msg_ou_usuario contém a mensagem de erro
    # Lógica para exibir as páginas após o login
    if "user_id" in st.session_state and st.session_state.page == "avaliacao":
        user_id = st.session_state.user_id
        st.subheader(f"Bem-vindo(a), {st.session_state.user_name}!")
        # Aqui você pode adicionar um sub-menu para Cadastro de Pets e Avaliações
        sub_menu_logado = st.sidebar.selectbox("Opções", ["Meus Pets e Avaliações", "Sair"])
        if sub_menu_logado == "Meus Pets e Avaliações":
            # Cadastro de Pets
            cadastro_pet_app(user_id)
            # Avaliações
            avaliacao_app(user_id)
        elif sub_menu_logado == "Sair":
            st.session_state.clear() # Limpa o estado da sessão
            st.rerun() # Redireciona para a página de login
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

        # Opções de tipo de usuário
        tipo_usuario_opcoes = ["Tutor", "Veterinário", "Clínica"]
        novo_tipo_usuario = st.selectbox("Tipo de Usuário", tipo_usuario_opcoes)

        # Campo para o país (com valor padrão)
        novo_pais = st.text_input("País", value="Brasil")

        submitted = st.form_submit_button("Registrar")

        if submitted:
            if nova_senha != confirmar_senha:
                st.error("As senhas não coincidem.")
            elif len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                ok, msg = cadastrar_usuario(novo_nome, novo_email, nova_senha, novo_tipo_usuario, novo_pais)
                if ok:
                    st.success(msg)
                    st.info("Você pode fazer login agora.")
                else:
                    st.error(msg)
# -------------------------------
# REDEFINIR SENHA
# -------------------------------
elif menu == "Redefinir Senha":
    st.subheader("Redefinir Senha")

    # Verifica se há um token na URL (para quando o usuário clica no link do e-mail)
    query_params = st.query_params
    token_url = query_params.get("token")

    if token_url:
        st.info("Você clicou em um link de redefinição de senha.")
        # 1. Validar o token e obter o e-mail do usuário
        token_valido_status, msg_validacao, email_usuario_reset = validar_token_reset(token_url)

        if token_valido_status and email_usuario_reset:
            st.success(f"Token válido para {email_usuario_reset}. Por favor, defina sua nova senha.")
            nova_senha_url = st.text_input("Nova senha", type="password", key="reset_nova_senha_url")
            confirmar_nova_senha_url = st.text_input("Confirmar nova senha", type="password", key="reset_confirmar_nova_senha_url")

            if st.button("Redefinir Senha", key="btn_redefinir_url"):
                if nova_senha_url != confirmar_nova_senha_url:
                    st.error("As senhas não coincidem.")
                elif len(nova_senha_url) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                else:
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
