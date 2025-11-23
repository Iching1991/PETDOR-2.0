# PETdor2/pages/confirmar_email.py

import streamlit as st
from PETdor2.auth.email_confirmation import confirmar_email


def render():
    st.title("📨 Confirmação de E-mail")

    token = st.query_params.get("token", None)

    if not token:
        st.error("Token não fornecido na URL.")
        return

    with st.spinner("Validando token..."):
        sucesso, msg = confirmar_email(token)

    if sucesso:
        st.success(msg)
        st.info("Agora você já pode fazer login.")

        # Ajuste para navegação interna do Streamlit
        if st.button("Ir para Login"):
            st.session_state.pagina = "login"
            st.experimental_rerun()

    else:
        st.error(msg)
        st.warning("Peça um novo link na página de login.")
