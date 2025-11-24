import sys
import os
import streamlit as st

# ==========================================================
# AJUSTE DE PATH (CORRETO E ÚNICO)
# ==========================================================

# Caminho do arquivo atual: .../PETdor2/streamlit_app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))           # /PETdor2
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))    # /mount/src/petdor2

# Garante que o diretório do app esteja no sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Garante que o diretório raiz também esteja no sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==========================================================
# IMPORTAÇÕES INTERNAS
# ==========================================================

from pages.login import render as login_app
from pages.cadastro import render as cadastro_app
from pages.avaliacao import render as avaliacao_app
from pages.cadastro_pet import render as cadastro_pet_app
from pages.historico import render as historico_app
from pages.admin import render as admin_app
from pages.conta import render as conta_app
from pages.confirmar_email import render as confirmar_email_app
from pages.password_reset import render as password_reset_app
from pages.recuperar_senha import render as recuperar_senha_app

from utils.notifications import verificar_confirmacao_email
from auth.security import usuario_logado, logout


# ==========================================================
# CONFIGURAÇÃO DO STREAMLIT
# ==========================================================

st.set_page_config(
    page_title="PetDor - Avaliação de Dor Animal",
    page_icon="🐾",
    layout="wide",
)


# ==========================================================
# SISTEMA DE NAVEGAÇÃO
# ==========================================================

def navegar():
    if "pagina" not in st.session_state:
        st.session_state.pagina = "login"

    pagina = st.session_state.pagina

    rotas = {
        "login": login_app,
        "cadastro": cadastro_app,
        "avaliacao": avaliacao_app,
        "cadastro_pet": cadastro_pet_app,
        "historico": historico_app,
        "admin": admin_app,
        "conta": conta_app,
        "confirmar_email": confirmar_email_app,
        "password_reset": password_reset_app,
        "recuperar_senha": recuperar_senha_app,
    }

    if pagina in rotas:
        rotas[pagina]()
    else:
        st.error(f"Página '{pagina}' não encontrada.")


# ==========================================================
# MENU LATERAL
# ==========================================================

def menu_lateral():
    with st.sidebar:
        st.title("🐾 PetDor")

        user = usuario_logado()

        if user:
            st.write(f"👋 Bem-vindo(a), **{user['email']}**")

            if st.button("🏠 Página Inicial"):
                st.session_state.pagina = "avaliacao"

            if st.button("🐶 Cadastrar Pet"):
                st.session_state.pagina = "cadastro_pet"

            if st.button("📜 Histórico"):
                st.session_state.pagina = "historico"

            if user.get("is_admin"):
                st.divider()
                if st.button("🛠 Área Administrativa"):
                    st.session_state.pagina = "admin"

            st.divider()

            if st.button("⚙ Minha Conta"):
                st.session_state.pagina = "conta"

            if st.button("🚪 Sair"):
                logout()
                st.session_state.pagina = "login"
                st.rerun()
        else:
            st.info("Faça login para acessar todas as funcionalidades.")


# ==========================================================
# APLICAÇÃO PRINCIPAL
# ==========================================================

def main():
    user = usuario_logado()

    if user:
        verificar_confirmacao_email(user)

    menu_lateral()
    navegar()


if __name__ == "__main__":
    main()
