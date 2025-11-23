# PETdor2/auth/email_confirmation.py
import logging
logger = logging.getLogger(__name__)

# ==========================
# Confirmar e-mail
# ==========================
def confirmar_email(token: str) -> tuple[bool, str]:
    """
    Valida token JWT e confirma o e-mail do usuário.
    Retorna (True, msg) ou (False, msg).
    """
    try:
        from database.supabase_client import supabase  # import local
        from auth.security import verify_email_token

        email = verify_email_token(token)
        if not email:
            return False, "Token inválido ou expirado."

        # Buscar usuário com token válido
        resp = supabase.table("usuarios").select("*")\
            .eq("email", email)\
            .eq("email_confirm_token", token)\
            .eq("email_confirmado", False)\
            .execute()

        if resp.error:
            logger.error(f"Erro ao consultar usuário: {resp.error.message}")
            return False, "Erro interno ao confirmar e-mail."

        if not resp.data:
            return False, "Token já utilizado ou não corresponde a nenhum usuário."

        usuario_id = resp.data[0]["id"]

        # Atualizar usuário para confirmado
        upd_resp = supabase.table("usuarios").update({
            "email_confirmado": True,
            "email_confirm_token": None
        }).eq("id", usuario_id).execute()

        if upd_resp.error:
            logger.error(f"Erro ao atualizar usuário {usuario_id}: {upd_resp.error.message}")
            return False, "Erro interno ao confirmar e-mail."

        return True, "E-mail confirmado com sucesso."

    except Exception:
        logger.error("Erro em confirmar_email", exc_info=True)
        return False, "Erro interno ao confirmar e-mail."


# ==========================
# Reenviar e-mail de confirmação
# ==========================
def reenviar_email_confirmacao(email: str) -> tuple[bool, str]:
    """
    Reenvia novo token para confirmação de e-mail.
    Nunca revela se o e-mail existe ou não.
    """
    try:
        from database.supabase_client import supabase  # import local
        from auth.security import generate_email_token
        from utils.email_sender import enviar_email_confirmacao as enviar_email  # função de envio de email
        from os import getenv

        # Buscar usuário
        resp = supabase.table("usuarios").select("*").eq("email", email.lower()).execute()
        if resp.error:
            logger.error(f"Erro ao consultar usuário {email}: {resp.error.message}")
            return False, "Erro interno ao reenviar e-mail de confirmação."

        if not resp.data:
            # Não revela se existe
            return True, "Se o e-mail estiver cadastrado, você receberá um link."

        usuario = resp.data[0]

        if usuario.get("email_confirmado"):
            return True, "Conta já confirmada."

        # Gerar novo token
        novo_token = generate_email_token(email)

        # Atualizar token no Supabase
        upd_resp = supabase.table("usuarios").update({
            "email_confirm_token": novo_token
        }).eq("id", usuario["id"]).execute()

        if upd_resp.error:
            logger.error(f"Erro ao atualizar token de usuário {usuario['id']}: {upd_resp.error.message}")
            return False, "Erro interno ao reenviar e-mail de confirmação."

        # Criar link de confirmação
        confirm_link = f"{getenv('STREAMLIT_APP_URL')}?action=confirm_email&token={novo_token}"

        # Enviar e-mail
        email_ok, msg = enviar_email(email, usuario["nome"], confirm_link)
        if email_ok:
            logger.info(f"E-mail de confirmação reenviado para {email}")
            return True, "E-mail de confirmação reenviado."
        else:
            logger.warning(f"Falha ao enviar e-mail de confirmação para {email}: {msg}")
            return False, "Erro ao enviar e-mail de confirmação."

    except Exception:
        logger.error("Erro em reenviar_email_confirmacao", exc_info=True)
        return False, "Erro interno ao reenviar e-mail."
