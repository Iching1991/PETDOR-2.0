# PETdor_2.0/pages/cadastro_pet.py

import streamlit as st
from database.connection import conectar_db
from especies.index import listar_especies, EspecieConfig # <-- CORREÇÃO: Importa de especies.index e adiciona EspecieConfig

# Função auxiliar para formatar o nome da espécie no selectbox
def format_especie_nome(especie_config: EspecieConfig) -> str:
    return especie_config.nome

def cadastrar_pet_db(tutor_id, nome, especie_id, raca, peso): # <-- Alterado 'especie' para 'especie_id'
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pets (tutor_id, nome, especie, raca, peso)
        VALUES (?, ?, ?, ?, ?)
    """, (tutor_id, nome, especie_id, raca, peso)) # <-- Passa especie_id para o banco
    conn.commit()
    conn.close()

def listar_pets_db(tutor_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pets WHERE tutor_id = ?", (tutor_id,))
    pets = cur.fetchall()
    conn.close()
    return pets

def app(user_id: int):
    st.header("🐾 Cadastro de Pet")
    if not user_id:
        st.warning("Você precisa estar logado para cadastrar pets.")
        return

    with st.form("form_cadastro_pet"):
        nome = st.text_input("Nome do pet")

        # Obtém a lista de configurações de espécies
        especies_disponiveis = listar_especies()

        # CORREÇÃO: Usa format_func para exibir o nome da espécie no selectbox
        # e armazena o objeto EspecieConfig selecionado
        especie_selecionada_config = st.selectbox(
            "Espécie",
            options=especies_disponiveis,
            format_func=format_especie_nome # <-- Usa a função auxiliar
        )

        raca = st.text_input("Raça (opcional)")
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Cadastrar Pet")

    if submitted:
        if not nome or not especie_selecionada_config: # Verifica se uma espécie foi selecionada
            st.error("Nome e espécie são obrigatórios.")
        else:
            try:
                # CORREÇÃO: Passa o especie_id para a função de cadastro no banco
                cadastrar_pet_db(user_id, nome, especie_selecionada_config.especie_id, raca, peso if peso > 0 else None)
                st.success(f"Pet '{nome}' cadastrado com sucesso.")
            except Exception as e:
                st.error(f"Erro ao cadastrar pet: {e}")

    st.markdown("---")
    st.subheader("Seus pets")
    pets = listar_pets_db(user_id)
    if not pets:
        st.info("Nenhum pet cadastrado ainda.")
    else:
        for p in pets:
            st.write(f"- **{p['nome']}** — {p['especie']} — {p['raca'] or 'Raça não informada'} — {p['peso'] or 'Peso não informado'} kg")
