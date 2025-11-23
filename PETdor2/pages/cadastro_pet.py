# PETdor2/pages/cadastro_pet.py
import sys
import os
import streamlit as st
from typing import List, Optional, Dict, Any

# --- Corrige importações para Streamlit Cloud ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim correção ---

# ==========================================================
# Helpers
# ==========================================================

def format_especie_nome(especie_cfg) -> str:
    """Formatador para exibir nome da espécie no selectbox."""
    return especie_cfg.nome

def cadastrar_pet_db(tutor_id: int, nome: str, especie_nome: str, raca: Optional[str]=None, peso: Optional[float]=None) -> bool:
    """Insere um novo pet no banco."""
    try:
        from database.connection import conectar_db  # import local
        conn = conectar_db()
        cur = conn.cursor()
        sql = """
            INSERT INTO pets (tutor_id, nome, especie, raca, peso)
            VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(sql, (tutor_id, nome, especie_nome, raca, peso))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao cadastrar pet: {e}")
        return False
    finally:
        conn.close()

def listar_pets_db(tutor_id: int) -> List[Dict[str, Any]]:
    """Lista pets do tutor."""
    try:
        from database.connection import conectar_db  # import local
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pets WHERE tutor_id = ?", (tutor_id,))
        pets = cur.fetchall()
        return pets
    except Exception as e:
        st.error(f"Erro ao listar pets: {e}")
        return []
    finally:
        conn.close()

def listar_especies_local():
    """Lista espécies usando import local para Streamlit Cloud."""
    from especies.index import listar_especies
    return listar_especies()

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
        especies = listar_especies_local()
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
            sucesso = cadastrar_pet_db(
                tutor_id=tutor_id,
                nome=nome,
                especie_nome=especie_cfg.nome,
                raca=raca or None,
                peso=peso if peso > 0 else None
            )
            if sucesso:
                st.success(f"Pet '{nome}' cadastrado com sucesso!")

    st.markdown("---")
    st.subheader("Seus pets")

    pets = listar_pets_db(tutor_id)
    if not pets:
        st.info("Nenhum pet cadastrado ainda.")
    else:
        for p in pets:
            nome_pet = p.get("nome") or "Nome não informado"
            especie_pet = p.get("especie") or "Espécie não informada"
            raca_pet = p.get("raca") or "Raça não informada"
            peso_pet = f"{p.get('peso')} kg" if p.get("peso") else "Peso não informado"
            st.write(f"- **{nome_pet}** — {especie_pet} — {raca_pet} — {peso_pet}")



