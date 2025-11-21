# PETdor_2.0/auth/password_reset.py

"""
Módulo para gerenciamento de recuperação e redefinição de senha.
"""

import uuid
from datetime import datetime, timedelta
import logging
import bcrypt

from database.connection import conectar_db
from database.models import buscar_usuario_por_email
from utils.email_sender import enviar_email_reset_senha  # FUNÇÃO CORRETA

logger = logging.getLogger(__name__)

# ============================================================
# 1. SOLICITAR RESET DE SENHA
# ============================================================
def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera token e envia o link para redefinir senha.
    """
    try:
        usuario = buscar_usuario_por_email(email)

        # Segurança: nunca revelamos se o email existe
        if not usuario:
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

        # Criar token
        token = str(uuid.uuid4())
        expiracao = datetime.now() + timedelta(hours=1)

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO password_resets (usuario_id, token, criado_em, utilizado)
            VALUES (?, ?, ?, 0)
        """, (usuario["id"], token, expiracao.strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        # Enviar email
        enviado = enviar_email_reset_senha(usuario["email"], usuario["nome"], token)

        if not enviado:
            logger.warning(f"Falha ao enviar e-mail de reset para {email}.")
            return False, "Erro ao enviar e-mail. Tente novamente mais tarde."

        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

    except Exception as e:
        logger.error(f"Erro ao solicitar reset de senha: {e}", exc_info=True)
        return False, "Erro interno ao processar a solicitação."


# ============================================================
# 2. VALIDAR TOKEN
# ============================================================
def validar_token_reset(token: str) -> tuple[bool, str, str | None]:
    """
    Verifica se o token é válido.
    Retorna: (status, mensagem, email_usuario)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT pr.id, pr.criado_em, pr.utilizado, u.email
            FROM password_resets pr
            JOIN usuarios u ON u.id = pr.usuario_id
            WHERE pr.token = ?
        """, (token,))
        
        row = cursor.fetchone()
        conn.close()

        if not row:
            return False, "Token inválido.", None

        reset_id, criado_em, utilizado, email = row

        # Verificar expiração (1h)
        criado_em_dt = datetime.strptime(criado_em, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > criado_em_dt + timedelta(hours=1):
            return False, "Token expirado. Solicite uma nova redefinição.", None

        if utilizado:
            return False, "Token já utilizado.", None

        return True, "Token válido!", email

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return False, "Erro interno ao validar token.", None


# ============================================================
# 3. REDEFINIR SENHA COM TOKEN
# ============================================================
def redefinir_senha_com_token(token: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine senha usando token válido.
    """
    try:
        # Validar token primeiro
        valido, msg, email = validar_token_reset(token)
        if not valido:
            return False, msg

        # Buscar usuário pelo e-mail
        usuario = buscar_usuario_por_email(email)
        if not usuario:
            return False, "Usuário não encontrado."

        # Gerar hash seguro
        senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()

        conn = conectar_db()
        cursor = conn.cursor()

        # Atualizar senha
        cursor.execute("UPDATE usuarios SET senha = ? WHERE email = ?", (senha_hash, email))

        # Marcar token como utilizado
        cursor.execute("UPDATE password_resets SET utilizado = 1 WHERE token = ?", (token,))

        conn.commit()
        conn.close()

        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao redefinir senha com token: {e}", exc_info=True)
        return False, "Erro ao redefinir senha."
