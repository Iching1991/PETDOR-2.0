# PETdor2/backend/pages/cadastro_pet.py
import streamlit as st
from typing import List, Optional, Dict, Any
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Importa as funções do Supabase Client
# A importação correta é de '.database.supabase_client' porque 'pages' e 'database'
# são subpacotes do mesmo nível (ambos dentro de 'backend').
from .database.supabase_client import supabase_table_insert, supabase_table_select
from ..especies.index import listar_especies  # lista de espécies local

# ==========================================================
# Helpers
# ==========================================================
def format_especie_nome(especie_cfg) -> str:
    """Formata nome da espécie no selectbox."""
    # Assumindo que especie_cfg é um objeto/dataclass com um atributo 'nome'
    return especie_cfg.nome

def cadastrar_pet_db(tutor_id: int, nome: str, especie_nome: str, raca: Optional[str]=None, peso: Optional[float]=None) -> bool:
    """Insere um novo pet no banco usando a API do Supabase."""
    try:
        # Prepara os dados para inserção no Supabase
        pet_data = {
            "tutor_id": tutor_id,
            "nome": nome,
            "especie": especie_nome,
            "raca": raca,
            "peso": peso
        }

        # Chama a função de inserção do Supabase Client
        sucesso, mensagem = supabase_table_insert("pets", pet_data)

        if not sucesso:
            st.error(f"Erro ao cadastrar pet no Supabase: {mensagem}")
            logger.error(f"Erro ao cadastrar pet no Supabase: {mensagem}")
            return False

        return True
    except Exception as e:
        st.error(f"Erro inesperado ao cadastrar pet: {e}")
        logger.error(f"Erro inesperado ao cadastrar pet: {e}")
        return False

def listar_pets_db(tutor_id: int) -> List[Dict[str, Any]]:
    """Lista pets do tutor usando a API do Supabase."""
    try:
        # Define os filtros para a consulta
        filtros = {"tutor_id": {"eq": tutor_id}}

        # Chama a função de seleção do Supabase Client
        sucesso, pets_data = supabase_table_select("pets", filtros=filtros)

        if not sucesso:
            st.error(f"Erro ao listar pets do Supabase: {pets_data}")
            logger.error(f"Erro ao listar pets do Supabase: {pets_data}")
            return []

        return pets_data
    except Exception as e:
        st.error(f"Erro inesperado ao listar pets: {e}")
        logger.error(f"Erro inesperado ao listar pets: {e}")
        return []

# ==========================================================
# Página principal
# ==========================================================
def render():
    st.header("🐾 Cadastro de Pet")
    user = st.session_state.get("usuario")

    if not user:
        st.warning("Faça login para cadastrar pets.")
        return

    tutor_id = user["id"]

    with st.form("form_cadastro_pet"):
        nome = st.text_input("Nome do pet", key="pet_nome_input") # Adicionado key para evitar problemas de re-render
        especies = listar_especies()

        # Garante que especies não está vazia antes de tentar selecionar
        if not especies:
            st.error("Nenhuma espécie configurada. Contate o administrador.")
            especie_cfg = None
        else:
            especie_cfg = st.selectbox(
                "Espécie",
                options=especies,
                format_func=format_especie_nome,
                key="pet_especie_select" # Adicionado key
            )

        raca = st.text_input("Raça (opcional)", key="pet_raca_input") # Adicionado key
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1, format="%.1f", key="pet_peso_input") # Adicionado key
        enviado = st.form_submit_button("Cadastrar Pet")

    if enviado:
        if not nome or not especie_cfg:
            st.error("Nome e espécie são obrigatórios.")
        else:
            sucesso = cadastrar_pet_db(
                tutor_id=tutor_id,
                nome=nome,
                especie_nome=especie_cfg.nome,
                raca=raca or None,
                peso=peso if peso > 0 else None
            )
            if sucesso:
                st.success(f"Pet '{nome}' cadastrado com sucesso!")
                # Para limpar o formulário após o sucesso, uma opção é usar st.rerun()
                # ou resetar os valores dos widgets se eles tiverem chaves (keys)
                # st.session_state["pet_nome_input"] = "" # Exemplo de como limpar, mas Streamlit pode ser complicado com forms
                # st.session_state["pet_raca_input"] = ""
                # st.session_state["pet_peso_input"] = 0.0
                st.rerun() # Reinicia o app para limpar o formulário e atualizar a lista de pets

    st.markdown("---")
    st.subheader("Seus pets cadastrados")
    pets = listar_pets_db(tutor_id)

    if not pets:
        st.info("Nenhum pet cadastrado ainda.")
    else:
        # Exibe os pets em um formato mais organizado usando st.expander
        for i, p in enumerate(pets):
            nome_pet = p.get("nome") or "Nome não informado"
            especie_pet = p.get("especie") or "Espécie não informada"
            raca_pet = p.get("raca") or "Raça não informada"
            peso_pet = f"{p.get('peso'):.1f} kg" if p.get("peso") else "Não informado"

            with st.expander(f"**{nome_pet}** ({especie_pet})"):
                st.write(f"**Raça:** {raca_pet}")
                st.write(f"**Peso:** {peso_pet}")
                # Adicione mais detalhes do pet aqui se houver
                # st.write(f"ID do Pet: {p.get('id')}") # Exemplo
            # st.markdown("---") # O expander já serve como separador visual
