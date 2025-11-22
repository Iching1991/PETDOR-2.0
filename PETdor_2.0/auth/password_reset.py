# PETdor_2_0/auth/password_reset.py (REWRITE COMPLETO PARA SUPABASE)

import logging
from datetime import datetime, timedelta
import uuid
import os

from database.connection import conectar_db
from ..utils.email_sender import enviar_email_reset_senha
from auth.security import hash_password

logger = logging.getLogger(__name__)

# Detecta se está usando PostgreSQL (Supabase)
USANDO_POSTGRES = bool(os.getenv("DB_HOST"))

# ============================================================
# 1) SOLICITAR RESET DE SENHA
# ============================================================
def solicitar_reset_senha(email: str):
    """
    Gera token de redefinição de senha, salva no banco
    e envia o e-mail com o link.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql_select = (
            "SELECT id, nome, email FROM usuarios WHERE email = %s"
            if USANDO_POSTGRES else
            "SELECT id, nome, email FROM usuarios WHERE email = ?"
        )
        cur.execute(sql_select, (email,))
        usuario = cur.fetchone()

        if not usuario:
            logger.warning(f"Tentativa de reset para email inexistente: {email}")
            return True

        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)

        sql_update = (
            "UPDATE usuarios SET reset_password_token=%s, reset_password_expires=%s WHERE id=%s"
            if USANDO_POSTGRES else
            "UPDATE usuarios SET reset_password_token=?, reset_password_expires=? WHERE id=?"
        )
        cur.execute(sql_update, (token, expires_at, usuario[0]))
        conn.commit()

        enviado = enviar_email_reset_senha(usuario[2], usuario[1], token)
        return True if enviado else False

    except Exception as e:
        logger.error(f"Erro no reset de senha ({email}): {e}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()


# ============================================================
# 2) VALIDAR TOKEN
# ============================================================
def validar_token_reset(token: str):
    """
    Retorna o e-mail se o token for válido.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql = (
            "SELECT email, reset_password_expires FROM usuarios WHERE reset_password_token=%s"
            if USANDO_POSTGRES else
            "SELECT email, reset_password_expires FROM usuarios WHERE reset_password_token=?"
        )
        cur.execute(sql, (token,))
        usuario = cur.fetchone()

        if not usuario:
            return None

        expires = usuario[1]
        if expires < datetime.utcnow():
            return None

        return usuario[0]

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()


# ============================================================
# 3) REDEFINIR SENHA VIA TOKEN
# ============================================================
def redefinir_senha_com_token(token: str, nova_senha: str):
    """
    Redefine a senha com um token válido.
    """
    conn = None
    try:
        email = validar_token_reset(token)
        if not email:
            return False, "Token inválido ou expirado."

        nova_hash = hash_password(nova_senha)

        conn = conectar_db()
        cur = conn.cursor()

        sql_update = (
            "UPDATE usuarios SET senha_hash=%s, reset_password_token=NULL, reset_password_expires=NULL WHERE email=%s"
            if USANDO_POSTGRES else
            "UPDATE usuarios SET senha_hash=?, reset_password_token=NULL, reset_password_expires=NULL WHERE email=?"
        )
        cur.execute(sql_update, (nova_hash, email))
        conn.commit()

        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}", exc_info=True)
        return False, "Erro interno ao redefinir senha."
    finally:
        if conn:
            conn.close()

