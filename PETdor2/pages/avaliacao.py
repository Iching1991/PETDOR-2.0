"""
📝 Página de Avaliação de Dor - PETdor
Integra sistema modular de espécies (especies/)
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Importa sistema modular de espécies
from PETdor2.especies import (
    get_especies_nomes,
    get_especie_config,
    get_escala_labels,
)

# Substitua qualquer import relativo
# de:
# from ..database.supabase_client import supabase
# para:
from PETdor2.database.supabase_client import supabase
from PETdor2.especies.index import get_especies_nomes, buscar_especie_por_id, get_escala_labels



# =====================================================================
# 📌 Função para salvar avaliação no Supabase
# =====================================================================
def salvar_avaliacao(usuario_id, pet_id, especie, data, pontuacao, detalhes):
    try:
        payload = {
            "usuario_id": usuario_id,
            "pet_id": pet_id,
            "especie": especie,
            "data": data,
            "pontuacao": pontuacao,
            "detalhes": json.dumps(detalhes)
        }

        resposta = supabase.table("avaliacoes").insert(payload).execute()

        if hasattr(resposta, "error") and resposta.error:
            st.error(f"Erro ao salvar avaliação: {resposta.error.message}")
            return False

        return True

    except Exception as e:
        st.error(f"Falha ao comunicar com o banco: {e}")
        return False


# =====================================================================
# 📌 UI PRINCIPAL
# =====================================================================
def render():
    st.title("📊 Avaliação de Dor")

    st.write("Preencha as informações abaixo:")

    # Usuario
    usuario_id = st.session_state.get("usuario_id", None)
    if usuario_id is None:
        st.error("⚠ Você precisa estar logado para acessar esta página.")
        return

    # Selecionar espécie
    especies = get_especies_nomes()
    especie = st.selectbox("Selecione a espécie:", especies)

    # Selecionar PET
    pet_id = st.text_input("ID do seu PET:")

    # Data
    data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Carrega config da espécie
    especie_config = get_especie_config(especie)
    labels_escala = get_escala_labels(especie)

    st.subheader("Escala de dor")

    pontuacao = st.slider(
        "Nível de dor:",
        min_value=0,
        max_value=len(labels_escala) - 1,
        format="%d"
    )

    st.write(f"**Descrição:** {labels_escala[pontuacao]}")

    # Perguntas específicas da espécie
    st.subheader("Avaliação comportamental:")

    respostas = {}
    for pergunta in especie_config["perguntas"]:
        respostas[pergunta] = st.selectbox(
            p

