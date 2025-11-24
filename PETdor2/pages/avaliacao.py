# PETdor2/pages/avaliacao.py

import os
import sys
import json
import streamlit as st
from datetime import datetime

# ============================================
# Garantir que PETdor2/ esteja no sys.path
# ============================================
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))  # PETdor2/
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# ============================================
# IMPORTS ABSOLUTOS – OBRIGATÓRIOS NO CLOUD
# ============================================
from PETdor2.database.connection import conectar_db
from PETdor2.database.models import Pet
from PETdor2.especies.index import (
    get_especies_nomes,
    buscar_especie_por_id,
    get_escala_labels
)

# ==========================================================
# Funções de acesso ao banco
# ==========================================================
def carregar_pets_do_usuario(usuario_id: int):
    """Retorna todos os pets cadastrados pelo usuário."""
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
    """Salva a avaliação na tabela `avaliacoes`."""
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO avaliacoes (
            pet_id, usuario_id, especie,
            respostas_json, pontuacao_total, criado_em
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        pet_id,
        usuario_id,
        especie,
        respostas_json,
        pontuacao_total,
        datetime.now()
    ))

    conn.commit()
    conn.close()


# ==========================================================
# Interface principal
# ==========================================================
def render():
    usuario = st.session_state.get("usuario")

    st.title("📋 Avaliação de Dor")

    if not usuario:
        st.warning("Faça login para acessar esta página.")
        return

    usuario_id = usuario["id"]

    # ----------------------------
    # Selecionar PET
    # ----------------------------
    st.subheader("🐾 Selecione o Pet")

    pets = carregar_pets_do_usuario(usuario_id)

    if not pets:
        st.info("Você ainda não cadastrou nenhum pet.")
        return

    opcoes_pet = {
        f"{p['nome']} ({p['especie']})": p["id"]
        for p in pets
    }

    escolha_pet = st.selectbox("Escolha o pet:", list(opcoes_pet.keys()))
    pet_id = opcoes_pet[escolha_pet]

    especie = next((p["especie"] for p in pets if p["id"] == pet_id), None)

    if not especie:
        st.error("⚠ Não foi possível identificar a espécie do pet.")
        return

    especie_cfg = buscar_especie_por_id(especie)

    if not especie_cfg:
        st.error(f"⚠ A espécie '{especie}' não possui escala configurada.")
        return

    st.subheader(f"🐶 Avaliação para espécie: **{especie}**")

    categorias = especie_cfg.get("categorias", [])
    respostas = {}
    pontuacao_total = 0

    # ----------------------------
    # Loop das perguntas
    # ----------------------------
    for categoria in categorias:
        st.markdown(f"### 🔹 {categoria['nome']}")

        for pergunta in categoria.get("perguntas", []):
            texto = pergunta["texto"]
            labels = get_escala_labels(pergunta["escala"])

            escolha = st.radio(
                texto,
                labels,
                key=f"{categoria['nome']}_{texto}"
            )

            respostas[texto] = escolha
            pontuacao_total += labels.index(escolha)

        st.divider()

    st.markdown(f"## 🧮 Pontuação Total: **{pontuacao_total}**")

    # ----------------------------
    # Botão Salvar
    # ----------------------------
    if st.button("Salvar Avaliação"):
        respostas_json = json.dumps(respostas, ensure_ascii=False)
        salvar_avaliacao(
            pet_id,
            usuario_id,
            especie,
            respostas_json,
            pontuacao_total
        )
        st.success("Avaliação salva com sucesso! ✅")
