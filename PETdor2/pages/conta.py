# PETdor2/pages/conta.py

import streamlit as st
from PETdor2.auth.user import (
    buscar_usuario_por_email,
    redefinir_senha,
    atualizar_status_usuario,
)
from PETdor2.database.connection import conectar_db


def atualizar_dados_usuario(user_id, nome, email):
    """Atualiza nome e email do usuário no banco."""
    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql = (
            "UPDATE usuarios SET nome=%s, email=%s WHERE id=%s"
            if st.session_state.USING_POSTGRES
            else "UPDATE usuarios SET nome=?, email=? WHERE id=?"
        )
        cur.execute(sql, (nome, email.lower(), user_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def render():
    st.header("👤 Minha Conta")

    usuario = st.session_state.get("usuario")

    if n
