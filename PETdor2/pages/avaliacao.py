# PETdor2/pages/avaliacao.py

import streamlit as st
from datetime import datetime
import json

# ===============================================
from PETdor2.database.supabase_client import supabase

from especies.index import (
    get_especies_nomes,
    buscar_especie_por_id,
    get_escala_labels
)


# ===============================================
# Acesso ao Banco de Dados - SUPABASE
# ===============================================
def carregar_pets_do_usuario(usuario_id: int) -> list[dict]:
    """Retorna todos os pets cadastrados pelo usuário via Supabase."""
    response = (
        supabase
        .from_("pets")
        .select("id, nome, especie")
        .eq("tutor_id", usuario_id)
        .order("nome", desc=False)
        .execute()
    )

    pets = response.data if getattr(response, "data", None) else []
    return pets


def salvar_avaliacao(pet_id: int, usuario_id: int, especie: str, respostas_json: str, pontuacao_total: int):
    """Salva a avaliação na tabela `avaliacoes` usando Supabase."""
    payload = {
        "pet_id": pet_id,
        "usuario_id": usuario_id,
        "especie": especie,
        "respostas_json": respostas_json,
        "pontuacao_total": pontuacao_total,
        "criado_em": datetime.utcnow().isoformat()
    }

    res = supabase.table("avaliacoes").insert(payload).execute()

    if getattr(res, "error", None):
        raise RuntimeError(f"Erro ao salvar avaliação: {res.error}")


# ===============================================
# Interface da Página
# ===============================================
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

    opcoes_pet = {
        f"{p.get('nome')} ({p.get('especie')})": p.get("id")
        for p in pets
    }

    escolha_pet = st.selectbox("Escolha o pet:", list(opcoes_pet.keys()))
    pet_id = opcoes_pet[escolha_pet]

    especie = next((p.get("especie") for p in pets if p.get("id") == pet_id), None)

    if not especie:
        st.error("⚠ Não foi possível identificar a espécie do pet.")
        return

    especie_cfg = buscar_especie_por_id(especie)

    if not especie_cfg:
        st.error(f"⚠ A espécie '{especie}' não possui escala configurada.")
        return

    st.subheader(f"🐶 Avaliação para espécie: **{especie_cfg['nome']}**")

    categorias = especie_cfg.get("categorias", [])
    respostas = {}
    pontuacao_total = 0

    # ----------------------------
    # Loop das Categorias
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

            try:
                pontuacao_total += labels.index(escolha)
            except ValueError:
                pontuacao_total += 0

        st.divider()

    st.markdown(f"## 🧮 Pontuação Total: **{pontuacao_total}**")

    # ----------------------------
    # Salvar Resultado
    # ----------------------------
    if st.button("Salvar Avaliação"):
        respostas_json = json.dumps(respostas, ensure_ascii=False)
        try:
            salvar_avaliacao(
                pet_id,
                usuario_id,
                especie,
                respostas_json,
                pontuacao_total
            )
            st.success("Avaliação salva com sucesso! ✅")
        except Exception as e:
            st.error(f"Erro ao salvar avaliação: {e}")

