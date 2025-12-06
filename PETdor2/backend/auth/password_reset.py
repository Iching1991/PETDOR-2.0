# PETdor2/backend/auth/password_reset.py
"""
Módulo de recuperação de senha - gerencia reset de senhas.
Usa tokens JWT com expiração de 1 hora.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any, Optional

# Importações absolutas a partir do pacote 'backend'
# Ajustado para os nomes das funções que definimos em auth.security
from .security import gerar_token_reset_senha, validar_token_reset_senha, hash_password
from utils.email_sender import enviar_email_recuperacao_senha
from database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Gera um token de reset de senha, armazena no DB e envia e-mail.
    """
    try:
        supabase = get_supabase()

        # 1. Buscar usuário
        response = supabase.from_("usuarios").select("id, nome, email").eq("email", email.lower()).single().execute()
        usuario = response.data

        if not usuario:
            logger.warning(f"Tentativa de reset de senha para e-mail não encontrado: {email}")
            # Por segurança, sempre retornar sucesso para não vazar informações de usuários existentes
            return True, "✅ Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha."

        usuario_id = usuario["id"]
        nome_usuario = usuario["nome"]

        # 2. Gerar token JWT
        # Usando a função renomeada de auth.security
        reset_token_jwt = gerar_token_reset_senha(usuario_id, email)

        # 3. Armazenar token e expiração no Supabase
        # A expiração do token no banco de dados deve ser a mesma do JWT para consistência
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1) # Token JWT expira em 1 hora

        update_response = (
            supabase
            .from_("usuarios")
            .update({
                "reset_password_token": reset_token_jwt,
                "reset_password_expires": expires_at.isoformat()
            })
            .eq("id", usuario_id)
            .execute()
        )

        if not update_response.data:
            logger.error(f"Erro ao armazenar token de reset para {email}: {update_response.status_code} - {update_response.text}")
            return False, "❌ Erro interno ao solicitar redefinição de senha."

        # 4. Enviar e-mail
        sucesso_email, msg_email = enviar_email_recuperacao_senha(
            destinatario_email=email,
            destinatario_nome=nome_usuario,
            token=reset_token_jwt
        )

        if not sucesso_email:
            logger.error(f"Falha ao enviar e-mail de recuperação de senha para {email}: {msg_email}")
            return False, "❌ Erro ao enviar e-mail de recuperação. Tente novamente mais tarde."

        logger.info(f"✅ Link de reset de senha enviado para {email}")
        return True, "✅ Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha."

    except Exception as e:
        logger.error(f"Erro em solicitar_reset_senha para {email}: {e}", exc_info=True)
        return False, f"❌ Erro interno ao solicitar redefinição de senha: {str(e)}"

def validar_token_reset(token: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Valida o token de reset de senha.
    Retorna (True, {"email": email, "usuario_id": id}) se válido,
    ou (False, {"erro": mensagem}) se inválido/expirado.
    """
    try:
        # 1. Validar o token JWT
        # Usando a função renomeada de auth.security
        payload = validar_token_reset_senha(token)
        if not payload:
            return False, {"erro": "Token inválido ou expirado."}

        usuario_id_jwt = payload.get("usuario_id")
        email_jwt = payload.get("email")

        if not usuario_id_jwt or not email_jwt:
            logger.warning(f"Token de reset inválido: payload incompleto. Payload: {payload}")
            return False, {"erro": "Token inválido (dados incompletos)."}

        # 2. Buscar usuário no banco e verificar token
        supabase = get_supabase()
        response = supabase.from_("usuarios").select("id, email, reset_password_token, reset_password_expires").eq("id", usuario_id_jwt).single().execute()
        usuario = response.data

        if not usuario:
            logger.warning(f"Usuário não encontrado para token de reset JWT ID: {usuario_id_jwt}")
            return False, {"erro": "Token inválido."} # Usuário não existe mais ou ID incorreto

        # Verifica se o token no banco corresponde ao token fornecido
        if usuario.get("reset_password_token") != token:
            logger.warning(f"Token de reset no banco não corresponde ao token fornecido para {email_jwt}")
            return False, {"erro": "Token inválido ou já utilizado."}

        email_db = usuario["email"]
        usuario_id = usuario["id"]
        expires_str = usuario["reset_password_expires"]

        # 3. Validar expiração no banco
        if expires_str:
            expires_dt = datetime.fromisoformat(expires_str).replace(tzinfo=timezone.utc) # Garante timezone-aware
            if expires_dt < datetime.now(timezone.utc):
                logger.warning(f"Token expirado no banco para {email_db}")
                return False, {"erro": "Token expirado. Solicite um novo link."}
        else:
            logger.warning(f"Token de reset sem data de expiração no banco para {email_db}")
            return False, {"erro": "Token inválido (expiração não definida)."}

        # 4. Validar consistência entre JWT e banco
        if email_jwt.lower() != email_db.lower():
            logger.warning(f"Email inconsistente: JWT={email_jwt}, DB={email_db}")
            return False, {"erro": "Token inválido."}

        logger.info(f"✅ Token de reset válido para {email_db}")
        return True, {"email": email_db, "usuario_id": usuario_id}

    except Exception as e:
        logger.error(f"Erro em validar_token_reset: {e}", exc_info=True)
        return False, {"erro": str(e)}

def redefinir_senha_com_token(token: str, nova_senha: str) -> Tuple[bool, str]:
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

        if not usuario_id:
            return False, "Erro interno: ID do usuário não encontrado no token."

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
                "reset_password_token": None, # Limpa o token após o uso
                "reset_password_expires": None # Limpa a expiração
            })
            .eq("id", usuario_id)
            .execute()
        )

        if not update_response.data:
            logger.error(f"Erro ao redefinir senha para {email}: {update_response.status_code} - {update_response.text}")
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

