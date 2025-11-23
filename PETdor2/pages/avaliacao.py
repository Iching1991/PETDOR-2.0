# PETdor2/pages/avaliacao.py

import sys
import os
import streamlit as st
from datetime import datetime

# --- Corrige importações para Streamlit Cloud ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim correção ---

# Importações locais
from database.connection import conectar_db
from database.models import Pet
from especies import (
    get_especies_nomes,
    buscar_especie_por_id,
    get_escala_labels,
)

# ==========================================================
# Carregar pets do usuário
# ==========================================================
def carregar_pets_do_usuario(usuario_id):
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


# ==========================================================
# Salvar avaliação no banco
# ==========================================================
def salvar_avaliacao(pet_id, usuario_id, especie, respostas_json, pontuacao_total):
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
# Interface principal da página
# ==========================================================
def render():
    usuario = st.session_state.get("usuario")

    st.title("📋 Avaliação de Dor")

    if usuario is None:
        st.warning("Faça login para acessar esta página.")
        return

    usuario_id = usuario["id"]

    # ---------------------------------------------
    # Selecionar PET
    # ---------------------------------------------
    st.subheader("🐾 Selecione o Pet")

    pets = carregar_pets_do_usuario(usuario_id)

    if not pets:
        st.info("Você ainda não cadastrou nenhum pet.")
        return

    nome_pets = {f"{p['nome']} ({p['especie']})": p["id"] for p in pets}

    pet_escolhido = st.selectbox("Escolha o pet:", list(nome_pets.keys()))
    pet_id = nome_pets.get(pet_escolhido)

    # ---------------------------------------------
    # Selecionar espécie → montar escala certa
    # ---------------------------------------------
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

    # ---------------------------------------------
    # Loop das categorias e perguntas
    # ---------------------------------------------
    for categoria in categorias:
        st.markdown(f"### 🔹 {categoria['nome']}")
        perguntas = categoria.get("perguntas", [])

        for pergunta in perguntas:
            texto = pergunta["texto"]
            labels = get_escala_labels(pergunta["escala"])

            escolha = st.radio(
                texto,
                labels,
                key=f"{categoria['nome']}_{texto}"
            )

            respostas[texto] = escolha
            pontuacao_total += labels.index(escolha)

        st.markdown("---")

    st.markdown(f"## 🧮 Pontuação Total: **{pontuacao_total}**")

    # ---------------------------------------------
    # BOTÃO SALVAR
    # ---------------------------------------------
    if st.button("Salvar Avaliação"):
        import json

        respostas_json = json.dumps(respostas, ensure_ascii=False)

        salvar_avaliacao(
            pet_id,
            usuario_id,
            especie,
            respostas_json,
            pontuacao_total
        )

        st.success("Avaliação salva com sucesso!")
