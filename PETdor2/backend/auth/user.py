# PETdor2/backend/auth/user.py

import bcrypt
import jwt
import datetime
from typing import Optional, Dict, Any, Tuple

from backend.database.supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
)

from backend.utils.email_sender import enviar_email_confirmacao


# ======================================================
# CONFIG
# ======================================================

JWT_SECRET = "secret"
JWT_EXP_DELTA = 86400 * 7  # 7 dias


# ======================================================
# HASH / VERIFY
# ======================================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ======================================================
# LOGIN
# ======================================================

def autenticar_usuario(email: str, senha: str) -> Tuple[bool, str, Optional[Dict]]:
    ok, usuario = supabase_table_select(
        "usuarios",
        filtros={"email": email},
        single=True
    )

    if not ok or not usuario:
        return False, "Usuário não encontrado.", None

    if not verify_password(senha, usuario["senha"]):
        return False, "Senha incorreta.", None

    token = gerar_token(usuario["id"])

    return True, token, usuario


# ======================================================
# TOKEN
# ======================================================

def gerar_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


# ======================================================
# CADASTRO
# ======================================================

def cadastrar_usuario(dados: Dict[str, Any]) -> Tuple[bool, str]:
    dados["senha"] = hash_password(dados["senha"])
    dados["email_confirmado"] = False

    ok, resp = supabase_table_insert("usuarios", dados)

    if not ok:
        return False, resp

    enviar_email_confirmacao(dados["email"], dados["nome"])

    return True, "Usuário cadastrado com sucesso."


# ======================================================
# CONFIRMAR EMAIL
# ======================================================

def confirmar_email(email: str) -> Tuple[bool, str]:
    return supabase_table_update(
        "usuarios",
        {"email_confirmado": True},
        {"email": email}
    )
