# PETdor_2_0/auth/password_reset.py

import logging
from datetime import datetime, timedelta
import uuid

from database.connection import conectar_db
from utils.email_sender import enviar_email_reset_senha  # NOME CORRETO!

logger = logging.getLogger(__name__)


# ============================================================
# 1) SOLICITAR RESET DE SENHA
# ============================================================
def solicitar_reset_senha(email: str):
    """
    Gera token de redefinição de senha, salva no banco
    e envia o e-mail com o link para o usuário.
    """
    conn = None
    try:
        conn = conectar_db()
        conn.row_factory = sqlite_dict  # Permite acessar por chave
        cur = conn.cursor()

        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cur.fetchone()

        if not usuario:
            # Segurança: nunca dizer que o e-mail não existe
            logger.warning(f"Tentativa de reset para email inexistente: {email}")
            return True

        # Gera token único
        token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=1)

        cur.execute("""
            UPDATE usuarios
            SET reset_password_token = ?, reset_password_expires = ?
            WHERE id = ?
        """, (token, expires_at.strftime("%Y-%m-%d %H:%M:%S"), usuario["id"]))

        conn.commit()

        # Envia o e-mail
        enviado = enviar_email_reset_senha(usuario["email"], usuario["nome"], token)

        if enviado:
            logger.info(f"Token enviado para: {email}")
            return True
        else:
            logger.error(f"Erro ao enviar email para: {email}")
            return False

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
    Retorna o e-mail se o token for válido e não estiver expirado.
    Caso contrário, retorna None.
    """
    conn = None
    try:
        conn = conectar_db()
        conn.row_factory = sqlite_dict
        cur = conn.cursor()

        cur.execute("""
            SELECT email, reset_password_expires
            FROM usuarios
            WHERE reset_password_token = ?
        """, (token,))
        usuario = cur.fetchone()

        if not usuario:
            return None

        # Converter string para datetime
        expires = datetime.strptime(usuario["reset_password_expires"], "%Y-%m-%d %H:%M:%S")

        if expires < datetime.now():
            logger.warning(f"Token expirado para email: {usuario['email']}")
            return None

        return usuario["email"]

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}", exc_info=True)
        return None

    finally:
        if conn:
            conn.close()


# ============================================================
# 3) REDEFINIR SENHA COM TOKEN
# ============================================================
def redefinir_senha_com_token(token: str, nova_senha: str):
    """
    Redefine a senha usando um token válido.
    """
    conn = None
    try:
        email = validar_token_reset(token)

        if not email:
            return False, "Token inválido ou expirado."

        # Import aqui para evitar import circular
        from .user import redefinir_senha
        sucesso, msg = redefinir_senha(email, nova_senha)

        if not sucesso:
            return False, msg

        # Limpa o token
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE usuarios
            SET reset_password_token = NULL,
                reset_password_expires = NULL
            WHERE email = ?
        """, (email,))
        conn.commit()

        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}", exc_info=True)
        return False, "Erro interno ao redefinir senha."

    finally:
        if conn:
            conn.close()


# ============================================================
# UTILIDADE: Row Factory para SQLite -> dict
# ============================================================
def sqlite_dict(cursor, row):
    """Converte rows em dict acessível por chave."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
