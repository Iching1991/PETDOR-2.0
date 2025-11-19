# PETdor_2.0/auth/password_reset.py

"""
Módulo para gerenciamento de recuperação e redefinição de senha.
"""

import uuid
from datetime import datetime, timedelta
import logging
import bcrypt

from database.connection import conectar_db
# Importa buscar_usuario_por_email do módulo models do pacote database
# ou, se você moveu para auth.user, importe de lá.
# Assumindo que está em database.models, como no seu models.py anterior.
from database.models import buscar_usuario_por_email

# Importa a função específica para envio de e-mail de recuperação
from utils.email_sender import enviar_email_recuperacao_senha

logger = logging.getLogger(__name__)

# -------------------------
# Solicitar recuperação de senha (usada por pages.recuperar_senha)
# -------------------------
def reset_password_request(email: str) -> tuple[bool, str]:
    """
    Gera um token de recuperação de senha e envia por e-mail.
    """
    try:
        usuario = buscar_usuario_por_email(email)
        if not usuario:
            # Para segurança, não informamos se o e-mail existe ou não
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

        token = str(uuid.uuid4())
        expiracao = datetime.now() + timedelta(hours=1) # Token válido por 1 hora

        conn = conectar_db()
        cursor = conn.cursor()
        # Inserir o token na tabela password_resets
        cursor.execute("""
            INSERT INTO password_resets (usuario_id, token, criado_em, utilizado)
            VALUES (?, ?, ?, 0)
        """, (usuario['id'], token, expiracao.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        # Envia o e-mail com o link de recuperação
        sucesso_email = enviar_email_recuperacao_senha(email, usuario['nome'], token)
        if not sucesso_email:
            logger.warning(f"Falha ao enviar e-mail de recuperação para {email}.")
            return False, "Erro ao enviar e-mail de recuperação. Tente novamente mais tarde."

        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

    except Exception as e:
        logger.exception(f"Erro ao solicitar recuperação de senha para {email}")
        return False, f"Ocorreu um erro inesperado: {e}"

# -------------------------
# Validar token de reset (usada por pages.reset_senha)
# -------------------------
def validar_token_reset(token: str) -> tuple[bool, int | None]:
    """
    Verifica se um token de recuperação de senha é válido e retorna o ID do usuário.
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT usuario_id, criado_em, utilizado
            FROM password_resets
            WHERE token = ?
        """, (token,))
        reset_info = cursor.fetchone()
        conn.close()

        if not reset_info:
            return False, None

        usuario_id, criado_em_str, utilizado = reset_info
        criado_em = datetime.strptime(criado_em_str, "%Y-%m-%d %H:%M:%S")

        if utilizado or (datetime.now() > (criado_em + timedelta(hours=1))):
            return False, None # Token já utilizado ou expirado

        return True, usuario_id

    except Exception as e:
        logger.exception(f"Erro ao validar token de reset: {token}")
        return False, None

# -------------------------
# Redefinir senha (usada por pages.reset_senha)
# -------------------------
def redefinir_senha(usuario_id: int, nova_senha: str, token_utilizado: str) -> bool:
    """
    Redefine a senha do usuário e invalida o token.
    """
    try:
        # Validação básica da nova senha (pode ser mais robusta com utils.validators)
        if not nova_senha or len(nova_senha) < 6: # Exemplo: mínimo de 6 caracteres
            logger.warning("Tentativa de redefinir senha com senha fraca para usuário %s", usuario_id)
            return False

        senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = conectar_db()
        cursor = conn.cursor()

        # Atualiza a senha do usuário
        cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, usuario_id)) # Assumindo coluna 'senha'

        # Marca o token como utilizado para evitar reuso
        cursor.execute("UPDATE password_resets SET utilizado = 1 WHERE token = ?", (token_utilizado,))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.exception(f"Erro ao redefinir senha para usuário {usuario_id} com token {token_utilizado}")
        return False
