# PETdor2/auth/password_reset.py
"""
Módulo de recuperação de senha - gerencia reset de senhas.
Usa tokens JWT com expiração de 1 hora.
"""
import logging
import os
from datetime import datetime, timedelta
from .security import generate_reset_token, verify_reset_token, hash_password
from utils.email_sender import enviar_email_reset_senha
from database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera token JWT de reset, salva no DB e envia e-mail.
    Retorna (True, msg) sempre que possível para não vazar existência.
    """
    try:
        supabase = get_supabase()

        # 1. Buscar usuário no Supabase
        response = (
            supabase
            .from_("usuarios")
            .select("id, nome, email")
            .eq("email", email.lower())
            .execute()
        )

        if not response.data:
            # Não revelar existência
            logger.warning(f"Tentativa de reset para e-mail não encontrado: {email}")
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

        usuario = response.data[0]
        usuario_id = usuario["id"]
        nome = usuario["nome"]
        email_db = usuario["email"]

        # 2. Gerar token JWT
        token = generate_reset_token(email_db)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # 3. Salvar token no Supabase
        update_response = (
            supabase
            .from_("usuarios")
            .update({
                "reset_password_token": token,
                "reset_password_expires": expires_at.isoformat()
            })
            .eq("id", usuario_id)
            .execute()
        )

        if not update_response.data:
            logger.error(f"Erro ao salvar token para {email_db}")
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

        # 4. Enviar e-mail
        try:
            reset_link = f"{os.getenv('STREAMLIT_APP_URL')}?action=reset_password&token={token}"
            enviado = enviar_email_reset_senha(email_db, nome, token)

            if enviado:
                logger.info(f"✅ E-mail de reset enviado para {email_db}")
            else:
                logger.warning(f"⚠️ Falha ao enviar e-mail de reset para {email_db}")

        except Exception as e:
            logger.warning(f"Erro ao enviar e-mail: {e}")

        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

    except Exception as e:
        logger.error(f"Erro em solicitar_reset_senha: {e}", exc_info=True)
        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

def validar_token_reset(token: str) -> str | None:
    """
    Verifica token JWT (via security) e também valida expiração registrada no banco.
    Retorna e-mail se válido, None caso contrário.
    """
    try:
        # 1. Primeiro valida JWT
        email = verify_reset_token(token)
        if not email:
            logger.warning("Token JWT inválido")
            return None

        # 2. Busca no Supabase
        supabase = get_supabase()

        response = (
            supabase
            .from_("usuarios")
            .select("email, reset_password_expires")
            .eq("reset_password_token", token)
            .single()
            .execute()
        )

        if not response.data:
            logger.warning(f"Token não encontrado no banco: {token}")
            return None

        usuario = response.data
        email_db = usuario["email"]
        expires_str = usuario["reset_password_expires"]

        # 3. Validar expiração
        if isinstance(expires_str, str):
            expires_dt = datetime.fromisoformat(expires_str)
        else:
            expires_dt = expires_str

        if expires_dt < datetime.utcnow():
            logger.warning(f"Token expirado para {email_db}")
            return None

        logger.info(f"✅ Token válido para {email_db}")
        return email_db

    except Exception as e:
        logger.error(f"Erro em validar_token_reset: {e}", exc_info=True)
        return None

def redefinir_senha_com_token(token: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine senha se token válido; limpa token no DB.
    """
    try:
        # 1. Validar token
        email = validar_token_reset(token)
        if not email:
            return False, "Token inválido ou expirado."

        # 2. Hash da nova senha
        hashed = hash_password(nova_senha)

        # 3. Atualizar Supabase
        supabase = get_supabase()

        update_response = (
            supabase
            .from_("usuarios")
            .update({
                "senha_hash": hashed,
                "reset_password_token": None,
                "reset_password_expires": None
            })
            .eq("email", email)
            .execute()
        )

        if not update_response.data:
            logger.error(f"Erro ao redefinir senha para {email}")
            return False, "Erro ao redefinir senha."

        logger.info(f"✅ Senha redefinida com sucesso para {email}")
        return True, "Senha redefinida com sucesso. Você já pode fazer login."

    except Exception as e:
        logger.error(f"Erro em redefinir_senha_com_token: {e}", exc_info=True)
        return False, "Erro interno ao redefinir senha."

__all__ = [
    "solicitar_reset_senha",
    "validar_token_reset",
    "redefinir_senha_com_token",
]
