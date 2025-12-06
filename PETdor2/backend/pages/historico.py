# PETdor2/pages/historico.py
"""
Página de histórico de avaliações do pet.
Exibe todas as avaliações realizadas pelo usuário logado.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import json

# 🔧 Imports absolutos
from backend.database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

# ==========================================================
# Funções de banco
# ==========================================================
def buscar_avaliacoes_usuario(usuario_id: int) -> list[dict]:
    """Busca todas as avaliações de um usuário e adiciona informações dos pets."""
    try:
        supabase = get_supabase()
        response = (
            supabase
            .from_("avaliacoes")
            .select("id, data_avaliacao, percentual_dor, observacoes, pet_id")
            .eq("usuario_id", usuario_id)
            .order("data_avaliacao", desc=True)
            .execute()
        )
        avaliacoes = response.data if response.data else []

        for aval in avaliacoes:
            try:
                pet_resp = supabase.from_("pets").select("nome, especie").eq("id", aval["pet_id"]).single().execute()
                aval["pet_nome"] = pet_resp.data.get("nome", "Desconhecido")
                aval["pet_especie"] = pet_resp.data.get("especie", "Desconhecida")
            except Exception as e:
                logger.warning(f"Erro ao buscar pet {aval.get('pet_id')}: {e}")
                aval["pet_nome"] = "Desconhecido"
                aval["pet_especie"] = "Desconhecida"

        return avaliacoes
    except Exception as e:
        logger.exception(f"Erro ao buscar avaliações para usuario_id={usuario_id}")
        return []

def deletar_avaliacao(avaliacao_id: int) -> tuple[bool, str]:
    """Deleta uma avaliação do banco de dados."""
    try:
        supabase = get_supabase()
        supabase.from_("avaliacoes").delete().eq("id", avaliacao_id).execute()
        logger.info(f"✅ Avaliação {avaliacao_id} deletada com sucesso")
        return True, "✅ Avaliação deletada com sucesso!"
    except Exception as e:
        logger.exception(f"Erro ao deletar avaliação {avaliacao_id}")
        return False, f"❌ Erro ao deletar avaliação: {e}"

# ==========================================================
# Renderização
# ==========================================================
def render():
    st.header("📊 Histórico de Avaliações")

    usuario = st.session_state.get("usuario")
    if not usuario:
        st.warning("⚠️ Faça login para acessar seu histórico.")
        st.session_state.pagina = "login"
        st.stop()

    usuario_id = usuario.get("id")
    avaliacoes = buscar_avaliacoes_usuario(usuario_id)

    if not avaliacoes:
        st.info("📭 Você ainda não registrou avaliações.")
        return

    st.success(f"✅ {len(avaliacoes)} avaliação(ões) encontrada(s)")
    st.divider()

    # Exibir avaliações em cards expansíveis
    for aval in avaliacoes:
        aval_id = aval.get("id")
        data = aval.get("data_avaliacao", "Data desconhecida")
        dor = aval.get("percentual_dor", 0)
        obs = aval.get("observacoes", "")
        pet_nome = aval.get("pet_nome", "Desconhecido")
        pet_esp = aval.get("pet_especie", "Desconhecida")

        # Formata a data
        try:
            data_obj = pd.to_datetime(data)
            data_formatada = data_obj.strftime("%d/%m/%Y %H:%M")
        except Exception:
            data_formatada = str(data)

        with st.expander(f"🐾 {pet_nome} — {pet_esp} — {data_formatada} — Dor: {dor}%"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"📅 **Data:** {data_formatada}")
                st.write(f"🐾 **Pet:** {pet_nome}")
                st.write(f"🏷️ **Espécie:** {pet_esp}")
            with col2:
                st.write(f"🔥 **Percentual de Dor:** {dor}%")
                st.progress(dor / 100)

            st.divider()
            st.write("📝 **Observações:**")
            st.write(obs if obs else "_Nenhuma observação registrada._")

            st.divider()
            col_delete, col_export = st.columns(2)

            with col_delete:
                if st.button("🗑️ Deletar avaliação", key=f"del_{aval_id}"):
                    sucesso, mensagem = deletar_avaliacao(aval_id)
                    if sucesso:
                        st.success(mensagem)
                        st.rerun()
                    else:
                        st.error(mensagem)

            with col_export:
                json_data = json.dumps({
                    "id": aval_id,
                    "pet": f"{pet_nome} ({pet_esp})",
                    "data": data_formatada,
                    "percentual_dor": dor,
                    "observacoes": obs
                }, ensure_ascii=False, indent=2)

                st.download_button(
                    label="📥 Exportar JSON",
                    data=json_data,
                    file_name=f"avaliacao_{aval_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=f"export_{aval_id}"
                )

    # Resumo geral
    st.divider()
    st.subheader("📈 Resumo Geral")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Avaliações", len(avaliacoes))
    with col2:
        dor_media = sum(a.get("percentual_dor", 0) for a in avaliacoes) / len(avaliacoes)
        st.metric("Dor Média", f"{dor_media:.1f}%")
    with col3:
        dor_maxima = max(a.get("percentual_dor", 0) for a in avaliacoes)
        st.metric("Dor Máxima Registrada", f"{dor_maxima}%")

__all__ = ["render"]
