"""
Página de cadastro de pets - PETDor2
Permite que tutores cadastrem e visualizem seus pets.
"""

import streamlit as st
from typing import List, Optional, Dict, Any
import logging

# 🔧 Configuração de logging
logger = logging.getLogger(__name__)

# 🔧 Imports absolutos do backend
from backend.database.supabase_client import supabase_table_insert, supabase_table_select
from backend.especies.index import listar_especies  # lista de espécies registradas localmente

# ==========================================================
# Helpers
# ==========================================================
def format_especie_nome(especie_cfg) -> str:
    """Formata nome da espécie no selectbox."""
    return especie_cfg.nome if hasattr(especie_cfg, "nome") else str(especie_cfg)

def cadastrar_pet_db(
    tutor_id: int,
    nome: str,
    especie_nome: str,
    raca: Optional[str] = None,
    peso: Optional[float] = None
) -> bool:
    """Insere um novo pet no banco usando Supabase."""
    try:
        pet_data = {
            "tutor_id": tutor_id,
            "nome": nome,
            "especie": especie_nome,
            "raca": raca,
            "peso": peso
        }

        sucesso, mensagem = supabase_table_insert("pets", pet_data)

        if not sucesso:
            st.error(f"❌ Erro ao cadastrar pet: {mensagem}")
            logger.error(f"Erro ao cadastrar pet no Supabase: {mensagem}")
            return False

        logger.info(f"✅ Pet '{nome}' cadastrado com sucesso para tutor_id={tutor_id}")
        return True

    except Exception as e:
        st.error(f"❌ Erro inesperado ao cadastrar pet: {e}")
        logger.exception(f"Erro inesperado ao cadastrar pet: {e}")
        return False

def listar_pets_db(tutor_id: int) -> List[Dict[str, Any]]:
    """Lista pets do tutor usando a API do Supabase."""
    try:
        filtros = {"tutor_id": {"eq": tutor_id}}
        sucesso, pets_data = supabase_table_select("pets", filtros=filtros)

        if not sucesso:
            st.error(f"❌ Erro ao listar pets: {pets_data}")
            logger.error(f"Erro ao listar pets do Supabase: {pets_data}")
            return []

        return pets_data or []

    except Exception as e:
        st.error(f"❌ Erro inesperado ao listar pets: {e}")
        logger.exception(f"Erro inesperado ao listar pets: {e}")
        return []

# ==========================================================
# Página principal
# ==========================================================
def render():
    st.header("🐾 Cadastro de Pet")
    usuario = st.session_state.get("usuario")

    if not usuario:
        st.warning("Faça login para cadastrar pets.")
        return

    tutor_id = usuario["id"]

    with st.form("form_cadastro_pet"):
        nome = st.text_input("Nome do pet", key="pet_nome_input")
        especies = listar_especies()

        if not especies:
            st.error("Nenhuma espécie configurada. Contate o administrador.")
            especie_cfg = None
        else:
            especie_cfg = st.selectbox(
                "Espécie",
                options=especies,
                format_func=format_especie_nome,
                key="pet_especie_select"
            )

        raca = st.text_input("Raça (opcional)", key="pet_raca_input")
        peso = st.number_input(
            "Peso (kg)",
            min_value=0.0,
            step=0.1,
            format="%.1f",
            key="pet_peso_input"
        )

        enviado = st.form_submit_button("Cadastrar Pet")

    if enviado:
        if not nome or not especie_cfg:
            st.error("❌ Nome e espécie são obrigatórios.")
        else:
            sucesso = cadastrar_pet_db(
                tutor_id=tutor_id,
                nome=nome,
                especie_nome=especie_cfg.nome,
                raca=raca or None,
                peso=peso if peso > 0 else None
            )
            if sucesso:
                st.success(f"✅ Pet '{nome}' cadastrado com sucesso!")
                st.rerun()  # Reinicia o app para limpar formulário e atualizar lista

    st.markdown("---")
    st.subheader("Seus pets cadastrados")
    pets = listar_pets_db(tutor_id)

    if not pets:
        st.info("Nenhum pet cadastrado ainda.")
    else:
        for p in pets:
            nome_pet = p.get("nome") or "Nome não informado"
            especie_pet = p.get("especie") or "Espécie não informada"
            raca_pet = p.get("raca") or "Raça não informada"
            peso_pet = f"{p.get('peso'):.1f} kg" if p.get("peso") else "Não informado"

            with st.expander(f"**{nome_pet}** ({especie_pet})"):
                st.write(f"**Raça:** {raca_pet}")
                st.write(f"**Peso:** {peso_pet}")

__all__ = ["render"]
