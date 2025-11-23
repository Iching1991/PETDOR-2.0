# PETdor2/auth/password_reset.py
import logging
import os
from datetime import datetime, timedelta

from PETdor2.database.connection import conectar_db
from PETdor2.utils.email_sender import enviar_email_reset_senha
from PETdor2.auth.security import generate_reset_token, verify_reset_token, hash_password

logger = logging.getLogger(__name__)
USING_POSTGRES = bool(os.getenv("DB_HOST"))


# ==========================================================
# Utilitário para acessar row como dict ou tuple
# ==========================================================
def get(row, key_or_index):
    if row is None:
        return None
    if isinstance(row, dict):
        return row.get(key_or_index)
    if isinstance(row, (tuple, list)):
        return row[key_or_index]
    return None


# ==========================================================
# Solicitar reset de senha
# ==========================================================
def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera token JWT, salva no DB e envia e-mail.
    Retorna sempre mensagem genérica para não vazar existência do e-mail.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql_select = (
            "SELECT id, nome, email FROM usuarios WHERE email = %s"
            if USING_POSTGRES else
            "SELECT id, nome, email FROM usuarios WHERE email = ?"
        )
        cur.execute(sql_select, (email.lower(),))
        row = cur.fetchone()

        # Nunca revelar se existe ou não
        if not row:
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

        usuario_id = get(row, 0) if not isinstance(row, dict) else get(row, "id")
        nome = get(row, 1) if not isinstance(row, dict) else get(row, "nome")
        email_db = get(row, 2) if not isinstance(row, dict) else get(row, "email")

        token = generate_reset_token(email_db)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        sql_update = (
            "UPDATE usuarios SET reset_password_token=%s, reset_password_expires=%s WHERE id=%s"
            if USING_POSTGRES else
            "UPDATE usuarios SET reset_password_token=?, reset_password_expires=? WHERE id=?"
        )

        value_expires = (
            expires_at if USING_POSTGRES else expires_at.strftime("%Y-%m-%d %H:%M:%S")
        )

        cur.execute(sql_update, (token, value_expires, usuario_id))
        conn.commit()

        ok = enviar_email_reset_senha(email_db, nome, token)
        if ok:
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."
        else:
            return False, "Erro ao enviar o e-mail de redefinição."

    except Exception:
        logger.error("Erro em solicitar_reset_senha", exc_info=True)
        return False, "Erro interno ao solicitar redefinição."

    finally:
        if conn:
            conn.close()


# ==========================================================
# Validar token
# ==========================================================
def validar_token_reset(token: str) -> str | None:
    """
    Valida token JWT e confirma expiração registrada no banco.
    Retorna email se válido, caso contrário None.
    """
    try:
        # Valida JWT primeiro
        email_jwt = verify_reset_token(token)
        if not email_jwt:
            return None

        conn = conectar_db()
        cur = conn.cursor()

        sql = (
            "SELECT email, reset_password_expires FROM usuarios WHERE reset_password_token = %s"
            if USING_POSTGRES else
            "SELECT email, reset_password_expires FROM usuarios WHERE reset_password_token = ?"
        )
        cur.execute(sql, (token,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        email_db = get(row, "email") if isinstance(row, dict) else get(row, 0)
        expires = get(row, "reset_password_expires") if isinstance(row, dict) else get(row, 1)

        # Normalizar data
        if isinstance(expires, str):
            try:
                expires_dt = datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
            except Exception:
                # Se falhar, confiar no exp do JWT
                return email_db
        else:
            expires_dt = expires

        if expires_dt < datetime.utcnow():
            return None

        return email_db

    except Exception:
        logger.error("Erro em validar_token_reset", exc_info=True)
        return None


# ==========================================================
# Redefinir senha
# ==========================================================
def redefinir_senha_com_token(token: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine senha e apaga token do banco.
    """
    conn = None
    try:
        email = validar_token_reset(token)
        if not email:
            return False, "Token inválido ou expirado."

        hashed_pw = hash_password(nova_senha)

        conn = conectar_db()
        cur = conn.cursor()

        sql = (
            "UPDATE usuarios SET senha_hash=%s, reset_password_token=NULL, reset_password_expires=NULL WHERE email=%s"
            if USING_POSTGRES else
            "UPDATE usuarios SET senha_hash=?, reset_password_token=NULL, reset_password_expires=NULL WHERE email=?"
        )
        cur.execute(sql, (hashed_pw, email))
        conn.commit()

        return True, "Senha redefinida com sucesso."

    except Exception:
        logger.error("Erro em redefinir_senha_com_token", exc_info=True)
        return False, "Erro interno ao redefinir senha."
    finally:
        if conn:
            conn.close()
