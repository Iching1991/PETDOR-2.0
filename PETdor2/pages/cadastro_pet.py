# PETdor2/pages/cadastro_pet.py
import sys
import os
import streamlit as st

# --- Corrige importações para Streamlit Cloud ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim correção ---

# Importações locais
from database.connection import conectar_db
from especies.index import listar_especies, EspecieConfig

# ==========================================================
# Helpers
# ==========================================================

def format_especie_nome(especie_cfg: EspecieConfig) -> str:
    """Formatador para exibir nome da espécie no selectbox."""
    return especie_cfg.nome

def cadastrar_pet_db(tutor_id, nome, especie_nome, raca, peso):
    """Insere um novo pet no banco."""
    conn = conectar_db()
    cur = conn.cursor()

    sql = """
        INSERT INTO pets (tutor_id, nome, especie, raca, peso)
        VALUES (?, ?, ?, ?, ?)
    """
    cur.execute(sql, (tutor_id, nome, especie_nome, raca, peso))
    conn.commit()
    conn.close()

def listar_pets_db(tutor_id):
    """Lista pets do tutor."""
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pets WHERE tutor_id = ?", (tutor_id,))
    pets = cur.fetchall()
    conn.close()
    return pets

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
        nome = st.text_input("Nome do pet")
        especies = listar_especies()
        especie_cfg = st.selectbox(
            "Espécie",
            options=especies,
            format_func=format_especie_nome
        )
        raca = st.text_input("Raça (opcional)")
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)

        enviado = st.form_submit_button("Cadastrar Pet")

    if enviado:
        if not nome or not especie_cfg:
            st.error("Nome e espécie são obrigatórios.")
        else:
            try:
                cadastrar_pet_db(
                    tutor_id=tutor_id,
                    nome=nome,
                    especie_nome=especie_cfg.nome,
                    raca=raca,
                    peso=peso if peso > 0 else None,
                )
                st.success(f"Pet '{nome}' cadastrado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao cadastrar pet: {e}")

    # ======================================================
    # Lista de pets já cadastrados
    # ======================================================
    st.markdown("---")
    st.subheader("Seus pets")

    pets = listar_pets_db(tutor_id)

    if not pets:
        st.info("Nenhum pet cadastrado ainda.")
    else:
        for p in pets:
            nome_pet = p["nome"]
            especie_pet = p["especie"]
            raca_pet = p["raca"] or "Raça não informada"
            peso_pet = f"{p['peso']} kg" if p["peso"] else "Peso não informado"

            st.write(f"- **{nome_pet}** — {especie_pet} — {raca_pet} — {peso_pet}")
