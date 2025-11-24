import streamlit as st
from auth.user import verificar_credenciais, buscar_usuario_por_email

def render():
    st.header("🔐 Login")

    # Se já está logado, mostrar resumo e botão de logout
    if st.session_state.get("usuario"):
        usuario = st.session_state.usuario
        st.success(f"Você já está logado como **{usuario['nome']}** ({usuario['email']}).")
        if st.button("Sair"):
            st.session_state.usuario = None
            st.session_state.pagina = "login"
            st.rerun()
        return

    # Formulário de login
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        ok, resultado = verificar_credenciais(email, senha)
        if not ok:
            st.error(resultado)
        else:
            # Usuário autenticado com sucesso
            st.session_state.usuario = resultado
            st.success("Login realizado com sucesso!")
            st.session_state.pagina = "avaliacao"  # Redireciona para avaliação
            st.rerun()

    st.markdown("---")

    # Links úteis
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Criar conta"):
            st.session_state.pagina = "cadastro"
            st.rerun()
    with col2:
        if st.button("Esqueci minha senha"):
            st.session_state.pagina = "recuperar_senha"
            st.rerun()

    st.markdown("""
        <br>
        <p style='text-align:center;'>
            Versão PETdor 2.0 — Sistema de avaliação de dor animal 🐾
        </p>
    """, unsafe_allow_html=True)
