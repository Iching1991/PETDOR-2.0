# PETdor2/auth/email_confirmation.py
"""
Módulo de confirmação de e-mail - gerencia tokens e confirmação.
"""
import logging
import os
from .security import generate_email_confirmation_token, verify_email_confirmation_token
from database.supabase_client import get_supabase
from utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)

def gerar_token_confirmacao(usuario_id: int, email: str) -> str:
    """Gera um token de confirmação de e-mail."""
    return generate_email_confirmation_token(usuario_id, email)

def validar_token_confirmacao(token: str) -> tuple[bool, int]:
    """
    Valida um token de confirmação.
    Retorna (True, usuario_id) se válido, (False, None) se inválido.
    """
    valido, usuario_id, email = verify_email_confirmation_token(token)
    return valido, usuario_id

def confirmar_email(usuario_id: int) -> tuple[bool, str]:
    """Marca o e-mail como confirmado no banco de dados."""
    try:
        supabase = get_supabase()

        response = (
            supabase
            .from_("usuarios")
            .update({"email_confirmado": True})
            .eq("id", usuario_id)
            .execute()
        )

        if response.data:
            logger.info(f"✅ E-mail confirmado para usuário {usuario_id}")
            return True, "✅ E-mail confirmado com sucesso!"
        else:
            return False, "❌ Erro ao confirmar e-mail."

    except Exception as e:
        logger.error(f"Erro ao confirmar e-mail: {e}", exc_info=True)
        return False, f"❌ Erro: {e}"

def enviar_confirmacao_email(usuario_id: int, email: str, nome: str) -> tuple[bool, str]:
    """
    Gera token e envia e-mail de confirmação.
    """
    try:
        supabase = get_supabase()

        # 1. Gera token
        token = gerar_token_confirmacao(usuario_id, email)

        # 2. Salva token no Supabase
        update_response = (
            supabase
            .from_("usuarios")
            .update({"email_confirm_token": token})
            .eq("id", usuario_id)
            .execute()
        )

        if not update_response.data:
            logger.error(f"Erro ao salvar token de confirmação para {email}")
            return False, "Erro ao gerar link de confirmação."

        # 3. Cria link de confirmação
        confirm_link = f"{os.getenv('STREAMLIT_APP_URL', 'http://localhost:8501')}?action=confirm_email&token={token}"

        # 4. Envia e-mail
        email_enviado, mensagem = enviar_email_confirmacao(email, nome, confirm_link)

        if email_enviado:
            logger.info(f"✅ E-mail de confirmação enviado para {email}")
            return True, "✅ E-mail de confirmação enviado com sucesso!"
        else:
            logger.warning(f"Erro ao enviar e-mail de confirmação para {email}: {mensagem}")
            return False, mensagem

    except Exception as e:
        logger.error(f"Erro em enviar_confirmacao_email: {e}", exc_info=True)
        return False, f"Erro ao enviar e-mail: {e}"

def reenviar_email_confirmacao(email: str) -> tuple[bool, str]:
    """
    Reenvia novo token para confirmação de e-mail.
    Nunca revela se o e-mail existe ou não.
    """
    try:
        supabase = get_supabase()

        # 1. Buscar usuário
        resp = (
            supabase
            .from_("usuarios")
            .select("id, nome, email, email_confirmado")
            .eq("email", email.lower())
            .execute()
        )

        if not resp.data:
            # Não revela se existe
            logger.warning(f"Tentativa de reenvio para e-mail não encontrado: {email}")
            return True, "Se o e-mail estiver cadastrado, você receberá um link."

        usuario = resp.data[0]

        # 2. Verifica se já está confirmado
        if usuario.get("email_confirmado"):
            logger.info(f"Tentativa de reenvio para e-mail já confirmado: {email}")
            return True, "Sua conta já foi confirmada."

        # 3. Gerar novo token
        novo_token = gerar_token_confirmacao(usuario["id"], email)

        # 4. Atualizar token no Supabase
        upd_resp = (
            supabase
            .from_("usuarios")
            .update({"email_confirm_token": novo_token})
            .eq("id", usuario["id"])
            .execute()
        )

        if not upd_resp.data:
            logger.error(f"Erro ao atualizar token de confirmação para {usuario['id']}")
            return False, "Erro ao gerar novo link de confirmação."

        # 5. Criar link de confirmação
        confirm_link = f"{os.getenv('STREAMLIT_APP_URL', 'http://localhost:8501')}?action=confirm_email&token={novo_token}"

        # 6. Enviar e-mail
        email_ok, msg = enviar_email_confirmacao(email, usuario["nome"], confirm_link)

        if email_ok:
            logger.info(f"✅ E-mail de confirmação reenviado para {email}")
            return True, "✅ E-mail de confirmação reenviado com sucesso!"
        else:
            logger.warning(f"Falha ao enviar e-mail de confirmação para {email}: {msg}")
            return True, "Se o e-mail estiver cadastrado, você receberá um link."

    except Exception as e:
        logger.error(f"Erro em reenviar_email_confirmacao: {e}", exc_info=True)
        return True, "Se o e-mail estiver cadastrado, você receberá um link."

__all__ = [
    "gerar_token_confirmacao",
    "validar_token_confirmacao",
    "confirmar_email",
    "enviar_confirmacao_email",
    "reenviar_email_confirmacao",
]
