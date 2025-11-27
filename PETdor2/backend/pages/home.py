import streamlit as st

def render():
    st.title("🏠 Página Inicial")
    
    usuario = st.session_state.get("usuario")

    if not usuario:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.session_state.pagina = "login"
        st.rerun()

    st.success(f"Bem-vindo, {usuario['nome']}!")

    st.write("Aqui ficará o dashboard, estatísticas, atalhos e funcionalidades principais.")

    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
