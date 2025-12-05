"""
STREAMLIT APP - PETDOR
Carrega o frontend, usa o backend e conecta com Supabase.
"""

import sys
import os
import streamlit as st

# ============================================================
# --- GARANTE QUE O PROJETO PETDOR2 SEJA ENXERGADO PELO PYTHON
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))             # PETdor2/backend
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))          # PETdor2
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")                    # PETdor2/frontend

# Adiciona ao PATH apenas se ainda não estiver
for path in [ROOT_DIR, FRONTEND_DIR]:
    if path not in sys.path:
        sys.path.append(path)

# ============================================================
# --- IMPORTAÇÕES DO BACKEND (AGORA OK)
# ============================================================

from backend.database import testar_conexao
from backend.database import supabase_table_select
from backend.database import supabase_table_insert
from backend.database import supabase_table_update

# Se tiver utilidades ou validações:
# from backend.validators import validar_algo
# from backend.notifications import enviar_email
# from backend.auth.security import autenticar_usuario

# ============================================================
# --- IMPORTA FRONTEND (PÁGINAS DO USUÁRIO)
# ============================================================

try:
    from frontend.pages.home import render as home_page
except:
    home_page = None

try:
    from frontend.pages.login import render as login_page
except:
    login_page = None

try:
    from frontend.pages.avaliacao import render as avaliacao_page
except:
    avaliacao_page = None

# ============================================================
# --- LAYOUT DO STREAMLIT
# ============================================================

st.set_page_config(
    page_title="PetDor",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🐾 PetDor 2.0")
st.caption("Sistema integrado de avaliação veterinária com Supabase.")

# ============================================================
# --- TESTE AUTOMÁTICO DE CONEXÃO
# ============================================================

st.sidebar.write("### 🔌 Status do Banco")

try:
    ok, msg = testar_conexao()
    if ok:
        st.sidebar.success("Conectado ao Supabase!")
    else:
        st.sidebar.error("Erro: " + msg)
except Exception as e:
    st.sidebar.error(f"Falha crítica: {e}")

# ============================================================
# --- SIDEBAR DE NAVEGAÇÃO
# ============================================================

pagina = st.sidebar.selectbox(
    "📄 Navegar para:",
    [
        "🏠 Início",
        "🔐 Login",
        "📋 Avaliação Pet",
        "📊 Banco (Debug)"
    ]
)

# ============================================================
# --- ROTAS / PÁGINAS
# ============================================================

if pagina == "🏠 Início":
    if home_page:
        home_page()
    else:
        st.warning("Página home não encontrada.")

elif pagina == "🔐 Login":
    if login_page:
        login_page()
    else:
        st.warning("Página de login não encontrada.")

elif pagina == "📋 Avaliação Pet":
    if avaliacao_page:
        avaliacao_page()
    else:
        st.warning("Página de avaliação não encontrada.")

elif pagina == "📊 Banco (Debug)":
    st.subheader("🔧 Testes diretos no Supabase")

    tabela = st.text_input("Nome da tabela", "usuarios")

    if st.button("Carregar registros"):
        try:
            dados = supabase_table_select(tabela)
            st.json(dados)
        except Exception as e:
            st.error(f"Erro: {e}")

# ============================================================
# --- FIM
# ============================================================
