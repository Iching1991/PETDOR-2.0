# PetDor2/pages/login.py
import streamlit as st
import logging

# ===============================
# Configuração de logging
# ===============================
logger = logging.getLogger(__name__)

# ===============================
# Importações absolutas a partir da raiz do projeto
# ===============================
from auth.user import verificar_credenciais, buscar_usuario_por_id
from utils.validators import validar_email
from auth.security import usuario_logado # Para verificar se já está logado

def render():
    """
    Renderiza a página de login.
    """
    st.header("🔐 Login")
    st.write("Acesse sua conta para continuar.")

    # Se o usuário já estiver logado, não mostra o formulário de login
    if usuario_logado(st.session_state):
        st.info("Você já está logado!")
        # O app principal (streamlit_app.py) cuidará do redirecionamento
        return

    with st.form("login_form"):
        email = st.text_input("E-mail", key="login_email_input").lower().strip()
        senha = st.text_input("Senha", type="password", key="login_senha_input")

        submitted = st.form_submit_button("Entrar")

        if submitted:
            # 1️⃣ Validação de e-mail
            if not email:
                st.error("❌ Por favor, digite seu e-mail.")
                return
            if not validar_email(email):
                st.error("❌ E-mail inválido.")
                return
            if not senha:
                st.error("❌ Por favor, digite sua senha.")
                return

            # 2️⃣ Autenticação via Supabase
            # A função verificar_credenciais agora retorna (True, user_data) ou (False, mensagem_erro)
            success, resultado = verificar_credenciais(email, senha)

            if success:
                user_data = resultado # user_data é o dicionário completo do usuário

                # Verifica se o e-mail está confirmado (se essa regra estiver ativa)
                if not user_data.get("email_confirmado", False):
                    st.warning("⚠️ Seu e-mail ainda não foi confirmado. Verifique sua caixa de entrada.")
                    # Opcional: Você pode forçar o logout aqui ou impedir o acesso a certas páginas
                    return

                # 3️⃣ Armazena dados do usuário no session_state
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user_data.get("id")
                st.session_state["user_data"] = user_data # Armazena todos os dados
                st.session_state["user_email"] = user_data.get("email")
                st.session_state["user_name"] = user_data.get("nome")
                st.session_state["is_admin"] = user_data.get("tipo") == "Admin" # Assumindo coluna 'tipo'

                st.success("✔ Login realizado com sucesso!")
                logger.info(f"Usuário {email} logado com sucesso. ID: {user_data.get('id')}")

                # Redireciona para a página principal do app após o login
                # O streamlit_app.py já cuida disso, mas podemos forçar aqui se necessário
                st.session_state.page = "Meus Pets e Avaliações" # Ou a página padrão após login
                st.rerun()  # Atualiza a página para refletir o estado de login
            else:
                st.error(resultado) # resultado agora é a mensagem de erro
                logger.warning(f"Falha no login para {email}: {resultado}")

    # Link para "Esqueceu sua senha?"
    st.markdown("---")
    st.markdown("Esqueceu sua senha? Clique [aqui](#) para redefinir.")
    # A lógica de redefinição de senha será tratada no streamlit_app.py ou em uma página dedicada
    # que pode ser acessada via um botão ou link específico.
