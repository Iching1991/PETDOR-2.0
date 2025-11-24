# PETdor2/auth/password_reset.py
"""
Módulo de recuperação de senha - gerencia reset de senhas.
Usa tokens JWT com expiração de 1 hora.
"""
import logging
from datetime import datetime, timedelta
from .security import generate_reset_token, verify_reset_token, hash_password
from utils.email_sender import enviar_email_recuperacao_senha
from database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera token JWT de reset, salva no DB e envia e-mail.
    Retorna (True, msg) sempre que possível para não vazar existência de e-mail.
    """
    try:
        supabase = get_supabase()

        # 1. Buscar usuário
        response = (
            supabase
            .from_("usuarios")
            .select("id, nome, email")
            .eq("email", email.lower())
            .execute()
        )

        if not response.data:
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
            reset_link = f"https://petdor.streamlit.app?page=password_reset&token={token}"
            enviado, msg = enviar_email_recuperacao_senha(email_db, nome, reset_link)
            if enviado:
                logger.info(f"✅ E-mail de reset enviado para {email_db}")
            else:
                logger.warning(f"⚠️ Falha ao enviar e-mail: {msg}")
        except Exception as e:
            logger.warning(f"Erro ao enviar e-mail: {e}")

        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

    except Exception as e:
        logger.error(f"Erro em solicitar_reset_senha: {e}", exc_info=True)
        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

def validar_token_reset(token: str) -> tuple[bool, dict]:
    """
    Valida token de reset de senha.

    Retorna:
        (True, {"email": email, "usuario_id": id}) se válido
        (False, {"erro": mensagem}) se inválido
    """
    try:
        # 1. Validar token JWT
        token_valido, payload = verify_reset_token(token)
        if not token_valido:
            logger.warning(f"Token JWT inválido ou expirado")
            return False, {"erro": "Token inválido ou expirado."}

        email_jwt = payload.get("email")

        # 2. Buscar no banco para validar expiração adicional
        supabase = get_supabase()
        response = (
            supabase
            .from_("usuarios")
            .select("id, email, reset_password_expires")
            .eq("reset_password_token", token)
            .single()
            .execute()
        )

        if not response.data:
            logger.warning(f"Token não encontrado no banco")
            return False, {"erro": "Token não encontrado."}

        usuario = response.data
        email_db = usuario["email"]
        usuario_id = usuario["id"]
        expires_str = usuario["reset_password_expires"]

        # 3. Validar expiração no banco
        if isinstance(expires_str, str):
            expires_dt = datetime.fromisoformat(expires_str)
        else:
            expires_dt = expires_str

        if expires_dt < datetime.utcnow():
            logger.warning(f"Token expirado para {email_db}")
            return False, {"erro": "Token expirado. Solicite um novo link."}

        # 4. Validar consistência entre JWT e banco
        if email_jwt != email_db:
            logger.warning(f"Email inconsistente: JWT={email_jwt}, DB={email_db}")
            return False, {"erro": "Token inválido."}

        logger.info(f"✅ Token válido para {email_db}")
        return True, {"email": email_db, "usuario_id": usuario_id}

    except Exception as e:
        logger.error(f"Erro em validar_token_reset: {e}", exc_info=True)
        return False, {"erro": str(e)}

def redefinir_senha_com_token(token: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine senha se token válido; limpa token no DB.
    """
    try:
        # 1. Validar token
        token_valido, dados = validar_token_reset(token)
        if not token_valido:
            return False, dados.get("erro", "Token inválido ou expirado.")

        email = dados.get("email")
        usuario_id = dados.get("usuario_id")

        # 2. Validar força da senha
        if len(nova_senha) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres."

        # 3. Hash da nova senha
        hashed = hash_password(nova_senha)

        # 4. Atualizar Supabase
        supabase = get_supabase()
        update_response = (
            supabase
            .from_("usuarios")
            .update({
                "senha_hash": hashed,
                "reset_password_token": None,
                "reset_password_expires": None
            })
            .eq("id", usuario_id)
            .execute()
        )

        if not update_response.data:
            logger.error(f"Erro ao redefinir senha para {email}")
            return False, "Erro ao redefinir senha."

        logger.info(f"✅ Senha redefinida com sucesso para {email}")
        return True, "✅ Senha redefinida com sucesso. Você já pode fazer login."

    except Exception as e:
        logger.error(f"Erro em redefinir_senha_com_token: {e}", exc_info=True)
        return False, "Erro interno ao redefinir senha."

__all__ = [
    "solicitar_reset_senha",
    "validar_token_reset",
    "redefinir_senha_com_token",
]
