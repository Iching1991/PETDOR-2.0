"""
Página de Avaliação de Dor - PETDor2
Permite que usuários logados avaliem a dor de seus pets com base na espécie.
"""

import streamlit as st
from datetime import datetime, timezone
import json
import logging
from typing import List, Dict, Any

# ============================================================
# 🔧 IMPORTS ABSOLUTOS
# ============================================================
from backend.database.supabase_client import get_supabase
from backend.especies.index import (
    get_especies_nomes,
    buscar_especie_por_id,
    get_escala_labels
)

logger = logging.getLogger(__name__)


# ============================================================
# 🔹 Funções utilitárias de acesso ao Supabase
# ============================================================

def carregar_pets_do_usuario(usuario_id: int) -> List[Dict[str, Any]]:
    """Retorna todos os pets cadastrados pelo usuário via Supabase."""
    try:
        supabase = get_supabase()

        response = (
            supabase
            .from_("pets")
            .select("id, nome, especie")
            .eq("tutor_id", usuario_id)
            .order("nome", desc=False)
            .execute()
        )

        pets = getattr(response, "data", None) or response.get("data") if isinstance(response, dict) else []
        return pets or []

    except Exception as e:
        logger.error(f"[ERRO] Falha ao carregar pets do usuário {usuario_id}: {e}", exc_info=True)
        st.error("❌ Erro ao carregar seus pets. Tente novamente.")
        return []


def salvar_avaliacao(pet_id: int, usuario_id: int, especie: str,
                     respostas_json: str, pontuacao_total: int) -> None:
    """Salva a avaliação na tabela `avaliacoes`."""
    try:
        supabase = get_supabase()

        payload = {
            "pet_id": pet_id,
            "usuario_id": usuario_id,
            "especie": especie,
            "respostas_json": respostas_json,
            "pontuacao_total": pontuacao_total,
            "criado_em": datetime.now(timezone.utc).isoformat()
        }

        supabase.from_("avaliacoes").insert(payload).execute()
        logger.info(f"✔ Avaliação salva com sucesso para pet_id={pet_id}")

    except Exception as e:
        logger.error(f"[ERRO] Falha ao salvar avaliação: {e}", exc_info=True)
        raise RuntimeError("Erro ao salvar avaliação. Contate o suporte.")


# ============================================================
# 🔹 Função principal da página
# ============================================================

def render():
    """Renderiza a página de avaliação de dor."""
    st.title("📋 Avaliação de Dor do Pet")

    # Sessão padronizada para user_data
    usuario = st.session_state.get("user_data")
    if not usuario:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        return

    usuario_id = usuario["id"]

    # ------------------------------------------------------------
    # 🐾 Seleção do Pet
    # ------------------------------------------------------------
    st.subheader("🐾 Selecione o Pet")

    pets = carregar_pets_do_usuario(usuario_id)

    if not pets:
        st.info("Você ainda não cadastrou nenhum pet.")
        if st.button("➕ Cadastrar Pet"):
            st.session_state.pagina = "cadastro_pet"
            st.rerun()
        return

    # Mapeia nomes para IDs
    opcoes_pet = {
        f"{p['nome']} ({p['especie']})": p["id"]
        for p in pets
    }

    nome_pet_escolhido = st.selectbox("Escolha o pet:", list(opcoes_pet.keys()))
    pet_id = opcoes_pet[nome_pet_escolhido]

    especie = next((p["especie"] for p in pets if p["id"] == pet_id), None)
    if not especie:
        st.error("⚠ Erro ao identificar a espécie do pet selecionado.")
        return

    especie_cfg = buscar_especie_por_id(especie)
    if not especie_cfg:
        st.error(f"⚠ A espécie '{especie}' não possui escala configurada.")
        return

    # ------------------------------------------------------------
    # 📋 Perguntas da avaliação
    # ------------------------------------------------------------
    st.subheader(f"🧪 Avaliação para: **{especie_cfg['nome']}**")

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

            # Soma pontuação baseada no índice do item
            try:
                pontuacao_total += labels.index(escolha)
            except Exception:
                pass

        st.divider()

    st.markdown(f"## 🧮 Pontuação Total: **{pontuacao_total}**")

    # ------------------------------------------------------------
    # 💾 Salvar Avaliação
    # ------------------------------------------------------------
    if st.button("💾 Salvar Avaliação"):
        try:
            respostas_json = json.dumps(respostas, ensure_ascii=False)
            salvar_avaliacao(pet_id, usuario_id, especie, respostas_json, pontuacao_total)
            st.success("✅ Avaliação salva com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao salvar avaliação: {e}")


__all__ = ["render"]
