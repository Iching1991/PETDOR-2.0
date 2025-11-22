# PetDor/pages/admin.py
import streamlit as st
from database.connection import conectar_db

def is_admin(user_id):
    # Implementação simples: usuário com id 1 é admin.
    # Troque por checagem real (campo is_admin) se adicionar na tabela.
    return user_id == 1

def listar_usuarios():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, ativo, data_criacao FROM usuarios ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def app():
    st.header("🔐 Administração")
    user_id = st.session_state.get("user_id")
    if not user_id or not is_admin(user_id):
        st.error("Acesso restrito a administradores.")
        return

    st.subheader("Usuários cadastrados")
    users = listar_usuarios()
    for u in users:
        st.write(f"- {u['id']}: **{u['nome']}** — {u['email']} — ativo: {bool(u['ativo'])} — {u['data_criacao']}")
