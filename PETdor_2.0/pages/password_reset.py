# PETdor_2.0/auth/password_reset.py

"""
Módulo para recuperação e redefinição de senha.
"""

import uuid
import logging
import bcrypt
from datetime import datetime, timedelta

from database.connection import conectar_db
from database.models import buscar_usuario_por_email
from utils.email_sender import enviar_email_reset_senha  # Função correta

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# 1) Solicitar recuperação de senha
# -----------------------------------------------------------
def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera um token de recuperação, salva no banco e envia o link por e-mail.
    """

    usuario = buscar_usuario_por_email(email)

    # Segurança: mesmo se não existir, responde igual
    if not usuario:
        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

    # Gera token único
    token = str(uuid.uuid4())
    expiracao = datetime.now() + timedelta(hours=1)

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO password_resets (usuario_id, token, criado_em, utilizado)
            VALUES (?, ?, ?, 0)
        """, (usuario.id, token, expiracao.strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

    except Exception as e:
        logger.error(f"Erro ao gerar token de reset: {e}")
        return False, "Erro interno ao gerar solicitação."

    # Envia o e-mail
    email_ok = enviar_email_reset_senha(email, usuario.nome, token)

    if not email_ok:
        logger.warning(f"Falha ao enviar e-mail para {email}.")
        return False, "Erro ao enviar o e-mail de recuperação."

    return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."


# -----------------------------------------------------------
# 2) Validar token do link
# -----------------------------------------------------------
def validar_token_reset(token: str) -> tuple[bool, str | int]:
    """
    Verifica se o token existe, não foi usado e está dentro do prazo.
    Retorna (True, usuario_id) se válido.
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT usuario_id, criado_em, utilizado
            FROM password_resets
            WHERE token = ?
        """, (token,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return False, "Token inválido."

        usuario_id, criado_em, utilizado = row

        # Se já foi utilizado
        if utilizado == 1:
            return False, "Token já utilizado."

        # Validade: 1 hora
        criado = datetime.strptime(criado_em, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > criado + timedelta(hours=1):
            return False, "Token expirado."

        return True, usuario_id

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return False, "Erro interno."


# -----------------------------------------------------------
# 3) Redefinir senha com token
# -----------------------------------------------------------
def redefinir_senha_com_token(token: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine a senha do usuário se o token for válido.
    """

    valido, resultado = validar_token_reset(token)

    if not valido:
        return False, resultado  # mensagem de erro

    usuario_id = resultado

    try:
        senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()

        conn = conectar_db()
        cursor = conn.cursor()

        # Atualiza senha do usuário
        cursor.execute("""
            UPDATE usuarios
            SET senha = ?
            WHERE id = ?
        """, (senha_hash, usuario_id))

        # Marca token como utilizado
        cursor.execute("""
            UPDATE password_resets
            SET utilizado = 1
            WHERE token = ?
        """, (token,))

        conn.commit()
        conn.close()

        return True, "Senha redefinida com sucesso."

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}")
        return False, "Erro interno ao redefinir senha."
