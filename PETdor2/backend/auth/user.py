# PETdor2/backend/auth/user.py

import bcrypt
import jwt
import datetime
import streamlit as st
from typing import Optional, Dict, Any

from backend.database.supabase_client import (
    supabase_table_insert,
    supabase_table_select,
    supabase_table_update,
)

SECRET_KEY = st.secrets["tokens"]["SECRET_KEY"]


# -----------------------------------------------------------
# 🔐 Criar Usuário
# -----------------------------------------------------------

def criar_usuario(nome: str, email: str, senha: str) -> Dict[str, Any]:
    """Cria um usuário no Supabase com hash de senha."""
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    success, data = supabase_table_insert(
        "usuarios",
        {
            "nome": nome,
            "email": email.lower(),
            "senha": hashed,
            "email_confirmado": False,
        }
    )

    return {"success": success, "data": data}


# -----------------------------------------------------------
# 🔐 Login
# -----------------------------------------------------------

def autenticar_usuario(email: str, senha: str) -> Dict[str, Any]:
    """Autentica usuário verificando hash da senha."""
    ok, user = supabase_table_select(
        "usuarios",
        filtros={"email": email.lower()},
        single=True
    )

    if not ok or not user:
        return {"success": False, "error": "Usuário não encontrado"}

    if not bcrypt.checkpw(senha.encode(), user["senha"].encode()):
        return {"success": False, "error": "Senha incorreta"}

    token = gerar_token({"user_id": user["id"]})

    return {"success": True, "token": token, "user": user}


# -----------------------------------------------------------
# 🔐 Gerar JWT
# -----------------------------------------------------------

def gerar_token(payload: dict) -> str:
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# -----------------------------------------------------------
# 🔐 Confirmar e-mail
# -----------------------------------------------------------

def confirmar_email(user_id: str) -> bool:
    ok, _ = supabase_table_update(
        "usuarios",
        {"email_confirmado": True},
        {"id": user_id}
    )
    return ok
