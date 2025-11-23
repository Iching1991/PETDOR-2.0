# PETdor2/pages/avaliacao.py

import sys
import os
import streamlit as st
from datetime import datetime
import json

# --- Corrige importações para Streamlit Cloud ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim correção ---

# Importações locais
from database.connection import conectar_db
from database.models import Pet
from especies.index import get_especies_nomes, buscar_especie_por_id, get_escala_labels

# ==========================================================
# Funções de acesso ao banco
# ==========================================================
def carregar_pets_do_usuario(usuario_id: int) -> list[dict]:
    """Retorna uma lista de pets cadastrados para o usuário."""
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, especie
        FROM pets
        WHERE tutor_id = ?
        ORDER BY nome
    """, (usuario_id,))
    pets = cur.fetchall()
    conn.close()
    return pets


def salvar_avaliacao(pet_id: int, usuario_id: int, especie: str, respostas_json: str, pontuacao_total: int):
    """Salva uma avaliação no banco de dados."""
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO avaliacoes (
            pet_id, usuario_id, especie, respostas_json, pontuacao_total, criado_em
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (pet_id, usuario_id, especie, respostas_json, pontuacao_total, datetime.now()))
    conn.commit()
    conn.close()


# ==========================================================
# Interface principal da página
# ==========================================================
def render():
    usuario = st.session_state.get("usuario")
    st.title("📋 Avaliação de Dor")

    if not usuario:
        st.warning("Faça login para acessar esta página.")
        return

    usuario_id = usuario["id"]

    # ----------------------------
    # Seleção do PET
    # ----------------------------
    st.subheader("🐾 Selecione o Pet")
    pets = carregar_pets_do_usuario(usuario_id)

    if not pets:
        st.info("Você ainda não cadastrou nenhum pet.")
        return

    pet_opcoes = {f"{p['nome']} ({p['especie']})": p["id"] for p in pets}
    pet_escolhido = st.selectbox("Escolha o pet:", list(pet_opcoes.keys()))
    pet_id = pet_opcoes[pet_escolhido]

    especie = next((p["especie"] for p in pets if p["id"] == pet_id), None)
    if not especie:
        st.error("Erro ao identificar a espécie do pet.")
        return

    especie_cfg = buscar_especie_por_id(especie)
    if not especie_cfg:
        st.error(f"A espécie '{especie}' não possui escala configurada.")
        return

    st.subheader(f"🐶 Avaliação para espécie: **{especie}**")

    categorias = especie_cfg.get("categorias", [])
    respostas = {}
    pontuacao_total = 0

    # ----------------------------
    # Loop de categorias e perguntas
    # ----------------------------
    for categoria in categorias:
        st.markdown(f"### 🔹 {categoria['nome']}")
        for pergunta in categoria.get("perguntas", []):
            texto = pergunta["texto"]
            labels = get_escala_labels(pergunta["escala"])

            escolha = st.radio(texto, labels, key=f"{categoria['nome']}_{texto}")
            respostas[texto] = escolha
            pontuacao_total += labels.index(escolha)

        st.markdown("---")

    st.markdown(f"## 🧮 Pontuação Total: **{pontuacao_total}**")

    # ----------------------------
    # Botão Salvar
    # ----------------------------
    if st.button("Salvar Avaliação"):
        respostas_json = json.dumps(respostas, ensure_ascii=False)
        salvar_avaliacao(pet_id, usuario_id, especie, respostas_json, pontuacao_total)
        st.success("Avaliação salva com sucesso!")
