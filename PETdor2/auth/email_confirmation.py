# PETdor2/auth/email_confirmation.py

import logging

from PETdor2.database.connection import conectar_db
from PETdor2.auth.security import verify_email_token
from PETdor2.utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)


def confirmar_email(token: str) -> bool:
    """
    Confirma o e-mail do usuário validando o token JWT.
    """
    try:
        # Valida o token JWT e obtém o e-mail dentro dele
        email = verify_email_token(token)
        if not email:
            logger.warning(f"Token inválido ou expirado na confirmação de e-mail: {token}")
            return False

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM usuarios 
            WHERE email = ? AND email_confirm_token = ? AND email_confirmado = 0
        """, (email, token))

        row = cursor.fetchone()
        if not row:
            conn.close()
            logger.warning("Token não corresponde a nenhum usuário ou já confirmado.")
            return False

        usuario_id = row["id"]

        # Confirma o e-mail
        cursor.execute("""
            UPDATE usuarios
            SET email_confirmado = 1,
                email_confirm_token = NULL
            WHERE id = ?
        """, (usuario_id,))

        conn.commit()
        conn.close()

        logger.info(f"E-mail confirmado com sucesso para usuário ID {usuario_id}")
        return True

    except Exception as e:
        logger.error(f"Erro ao confirmar e-mail: {e}", exc_info=True)
        return False


def reenviar_email_confirmacao(email: str) -> bool:
    """
    Reenvia o e-mail de confirmação para usuários não confirmados.
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email_confirm_token, email_confirmado
            FROM usuarios
            WHERE email = ?
        """, (email.lower(),))

        row = cursor.fetchone()
        conn.close()

        if not row:
            # Não revelar se o e-mail não existe
            return True

        usuario_id = row["id"]
        nome = row["nome"]
        token_existente = row["email_confirm_token"]
        confirmado = row["email_confirmado"]

        # Se já confirmado, nada a reenviar
        if confirmado == 1:
            logger.info(f"Usuário {email} já está confirmado. Nenhum envio necessário.")
            return True

        if not token_existente:
            logger.warning(f"Usuário {email} não possui token de confirmação salvo.")
            return False

        # Reenvia o e-mail
        ok_envio = enviar_email_confirmacao(email, nome, token_existente)

        if ok_envio:
            logger.info(f"E-mail de confirmação reenviado para {email}")
            return True
        else:
            logger.error(f"Falha ao reenviar e-mail para {email}")
            return False

    except Exception as e:
        logger.error(f"Erro ao reenviar confirmação: {e}", exc_info=True)
        return False
