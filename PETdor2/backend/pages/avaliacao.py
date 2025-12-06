"""
Página de avaliação de dor - PETDor2
Permite que usuários logados avaliem a dor de seus pets com base na espécie.
"""

import streamlit as st
from datetime import datetime
import json
import logging
from typing import List, Dict

# ============================================================
# 🔧 IMPORTS ABSOLUTOS (a partir do pacote backend)
# ============================================================
from backend.database.supabase_client import supabase
from backend.especies.index import get_especies_nomes, buscar_especie_por_id, get_escala_labels

logger = logging.getLogger(__name__)

# ============================================================
# Funções de acesso a dados
# ============================================================

def carregar_pets_do_usuario(usuario_id: int) -> List[Dict]:
    """Retorna todos os pets cadastrados pelo usuário via Supabase."""
    try:
        response = (
            supabase
            .from_("pets")
            .select("id, nome, especie")
            .eq("tutor_id", usuario_id)
            .order("nome", desc=False)
            .execute()
        )
        # Compatibilidade com versões de response diferentes
        pets = getattr(response, "data", None) or (response.get("data") if isinstance(response, dict) else None)
        return pets or []
    except Exception as e:
        logger.error(f"Erro ao carregar pets: {e}")
        st.error(f"❌ Erro ao carregar pets: {e}")
        return []

def salvar_avaliacao(pet_id: int, usuario_id: int, especie: str, respostas_json: str, pontuacao_total: int):
    """Salva a avaliação na tabela `avaliacoes` usando Supabase."""
    try:
        payload = {
            "pet_id": pet_id,
            "usuario_id": usuario_id,
            "especie": especie,
            "respostas_json": respostas_json,
            "pontuacao_total": pontuacao_total,
            "criado_em": datetime.utcnow().isoformat()
        }
        supabase.table("avaliacoes").insert(payload).execute()
        logger.info(f"✅ Avaliação salva com sucesso para pet_id={pet_id}")
    except Exception as e:
        logger.error(f"Erro ao salvar avaliação: {e}")
        raise RuntimeError(f"Erro ao salvar avaliação: {e}")

# ============================================================
# Função principal de renderização
# ============================================================

def render():
    """Renderiza a página de avaliação de dor."""
    usuario = st.session_state.get("usuario")
    st.title("📋 Avaliação de Dor")

    if not usuario:
        st.warning("Faça login para acessar esta página.")
        return

    usuario_id = usuario["id"]

    # ==============================
    # Seleção do PET
    # ==============================
    st.subheader("🐾 Selecione o Pet")
    pets = carregar_pets_do_usuario(usuario_id)

    if not pets:
        st.info("Você ainda não cadastrou nenhum pet.")
        if st.button("➕ Cadastrar Pet Agora"):
            st.session_state.pagina = "cadastro_pet"
            st.rerun()
        return

    opcoes_pet = {f"{p.get('nome')} ({p.get('especie')})": p.get("id") for p in pets}
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

    # ==============================
    # Loop de avaliação
    # ==============================
    st.subheader(f"🐶 Avaliação para espécie: **{especie_cfg['nome']}**")
    categorias = especie_cfg.get("categorias", [])
    respostas: Dict[str, str] = {}
    pontuacao_total = 0

    for categoria in categorias:
        st.markdown(f"### 🔹 {categoria['nome']}")
        for pergunta in categoria.get("perguntas", []):
            texto = pergunta["texto"]
            labels = get_escala_labels(pergunta["escala"])
            escolha = st.radio(texto, labels, key=f"{categoria['nome']}_{texto}")
            respostas[texto] = escolha
            try:
                pontuacao_total += labels.index(escolha)
            except ValueError:
                pontuacao_total += 0
        st.divider()

    st.markdown(f"## 🧮 Pontuação Total: **{pontuacao_total}**")

    # ==============================
    # Botão para salvar
    # ==============================
    if st.button("💾 Salvar Avaliação"):
        respostas_json = json.dumps(respostas, ensure_ascii=False)
        try:
            salvar_avaliacao(pet_id, usuario_id, especie, respostas_json, pontuacao_total)
            st.success("✅ Avaliação salva com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao salvar avaliação: {e}")

__all__ = ["render"]
