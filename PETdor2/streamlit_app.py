# streamlit_app.py

import streamlit as st
from backend.database import testar_conexao

st.set_page_config(page_title="PETdor", page_icon="🐾", layout="wide")

# Teste opcional de conexão
testar_conexao()

st.success("Backend carregado com sucesso! Use o menu lateral para navegar.")
