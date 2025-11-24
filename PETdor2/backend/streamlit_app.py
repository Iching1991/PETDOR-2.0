# PETdor2/streamlit_app.py
"""
PETDor - Avaliação de Dor Animal
Aplicação Streamlit para avaliação de dor em pets
"""
import streamlit as st
from PIL import Image
import os

# Configuração da página
st.set_page_config(
    page_title="PETDor - Avaliação de Dor Animal",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .header-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .header-logo {
        width: 80px;
        height: 80px;
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a7a6e;
    }
    </style>
""", unsafe_allow_html=True)

# Carrega a logo
logo_path = "assets/petdor-logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
else:
    logo = None

# Header com logo
col1, col2 = st.columns([1, 5])
with col1:
    if logo:
        st.image(logo, width=80)
    else:
        st.write("🐾")

with col2:
    st.title("PETDor - Avaliação de Dor Animal")
    st.markdown("*Avaliação profissional de dor em animais de companhia*")

st.divider()

# Inicializa session state
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

# Sidebar com navegação
with st.sidebar:
    if logo:
        st.image(logo, width=100)

    st.markdown("---")

    if st.session_state.usuario:
        st.success(f"✅ Bem-vindo, {st.session_state.usuario.get('nome', 'Usuário')}!")
        st.markdown(f"**E-mail:** {st.session_state.usuario.get('email', 'N/A')}")
        st.markdown(f"**Tipo:** {st.session_state.usuario.get('tipo', 'N/A').capitalize()}")

        st.markdown("---")

        # Menu de navegação
        pagina = st.radio(
            "📋 Menu",
            ["Dashboard", "Nova Avaliação", "Histórico", "Minha Conta", "Sair"],
            key="menu_nav"
        )

        if pagina == "Dashboard":
            st.session_state.pagina = "dashboard"
        elif pagina == "Nova Avaliação":
            st.session_state.pagina = "avaliacao"
        elif pagina == "Histórico":
            st.session_state.pagina = "historico"
        elif pagina == "Minha Conta":
            st.session_state.pagina = "conta"
        elif pagina == "Sair":
            st.session_state.usuario = None
            st.session_state.pagina = "login"
            st.rerun()

        # Admin menu (apenas para admins)
        if st.session_state.usuario.get("is_admin", False):
            st.markdown("---")
            st.markdown("### 🔧 Admin")
            if st.button("👥 Gerenciar Usuários"):
                st.session_state.pagina = "admin_usuarios"
            if st.button("📊 Relatórios"):
                st.session_state.pagina = "admin_relatorios"

    else:
        st.info("👤 Faça login para continuar")
        pagina = st.radio(
            "🔐 Autenticação",
            ["Login", "Cadastro"],
            key="auth_nav"
        )

        if pagina == "Login":
            st.session_state.pagina = "login"
        elif pagina == "Cadastro":
            st.session_state.pagina = "cadastro"

# Roteamento de páginas
if st.session_state.pagina == "login":
    from pages.login import render
    render()

elif st.session_state.pagina == "cadastro":
    from pages.cadastro import render
    render()

elif st.session_state.pagina == "dashboard":
    if st.session_state.usuario:
        from pages.dashboard import render
        render()
    else:
        st.warning("⚠️ Você precisa estar autenticado!")
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "avaliacao":
    if st.session_state.usuario:
        from pages.avaliacao import render
        render()
    else:
        st.warning("⚠️ Você precisa estar autenticado!")
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "historico":
    if st.session_state.usuario:
        from pages.historico import render
        render()
    else:
        st.warning("⚠️ Você precisa estar autenticado!")
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "conta":
    if st.session_state.usuario:
        from pages.conta import render
        render()
    else:
        st.warning("⚠️ Você precisa estar autenticado!")
        st.session_state.pagina = "login"
        st.rerun()

elif st.session_state.pagina == "admin_usuarios":
    if st.session_state.usuario and st.session_state.usuario.get("is_admin"):
        from pages.admin_usuarios import render
        render()
    else:
        st.error("❌ Acesso negado!")

elif st.session_state.pagina == "admin_relatorios":
    if st.session_state.usuario and st.session_state.usuario.get("is_admin"):
        from pages.admin_relatorios import render
        render()
    else:
        st.error("❌ Acesso negado!")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🐾 PETDor - Avaliação de Dor Animal</p>
        <p>© 2025 - Desenvolvido com ❤️ para o bem-estar dos animais</p>
    </div>
""", unsafe_allow_html=True)
