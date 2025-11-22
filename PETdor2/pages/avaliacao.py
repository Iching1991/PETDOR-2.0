# PETdor_2.0/pages/avaliacao.py

import streamlit as st
from database.connection import conectar_db
from database.models import Pet
from especies import buscar_especie_por_id, get_especies_nomes # <-- CORREÇÃO: Importa de 'especies'
from datetime import datetime

# ... (o restante do seu código para a página de avaliação) ...

# Exemplo de como você usaria as funções (apenas para referência, não precisa mudar se já estiver assim)
def app(user_id: int):
    st.header("📋 Avaliar Pet")

    if not user_id:
        st.warning("Você precisa estar logado para realizar avaliações.")
        return

    # Exemplo de uso de get_especies_nomes
    nomes_especies = get_especies_nomes()
    # ... (restante da sua lógica) ...

    # Exemplo de uso de buscar_especie_por_id
    # especie_config = buscar_especie_por_id(especie_id_selecionada)
    # ... (restante da sua lógica) ...
