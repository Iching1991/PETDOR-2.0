# PETdor2/auth/password_reset.py
import logging
from datetime import datetime, timedelta
import os
from database.supabase_client import supabase
from auth.security import generate_reset_token, verify_reset_token, hash_password
from utils.email_sender import enviar_email_recuperacao_senha

logger = logging.getLogger(__name__)

# ==========================
# Solicitar reset de senha
# ==========================
def solicitar_reset_senha(email):
    """
    Gera um token de redefinição de senha para o e-mail fornecido e envia um e-mail.
    """
    # 1. Buscar usuário no Supabase
    resp = supabase.table("usuarios").select("*").eq("email", email).execute()
    if resp.error:
        logger.error(f"Erro ao buscar usuário {email}: {resp.error.message}")
        return False, "Erro interno ao processar solicitação."

    if not resp.data:
        # Retornamos mensagem genérica por segurança
        logger.warning(f"Tentativa de reset de senha para e-mail não encontrado: {email}")
        return True, "Se o e-mail estiver registrado, um link de redefinição de senha foi enviado."

    usuario = resp.data[0]

    # 2. Gerar token e data de expiração
    token = generate_reset_token(email)
    expires_at = datetime.now() + timedelta(hours=1)

    # 3. Atualizar Supabase com token e expiração
    update_resp = supabase.table("usuarios").update({
        "reset_password_token": token,
        "reset_password_expires": expires_at.isoformat()
    }).eq("id", usuario["id"]).execute()

    if update_resp.error:
        logger.error(f"Erro ao salvar token para {email}: {update_resp.error.message}")
        return False, "Erro interno ao processar solicitação."

    # 4. Enviar e-mail
    try:
        reset_link = f"{os.getenv('STREAMLIT_APP_URL')}?action=reset_password&token={token}"
        email_enviado, msg_email = enviar_email_recuperacao_senha(usuario["email"], usuario["nome"], reset_link)
        if email_enviado:
            logger.info(f"E-mail de redefinição enviado para {email}.")
        else:
            logger.warning(f"Falha ao enviar e-mail de redefinição para {email}: {msg_email}")
        return True, "Se o e-mail estiver registrado, um link de redefinição de senha foi enviado."
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de redefinição para {email}: {e}", exc_info=True)
        return True, "Link de redefinição gerado, mas houve problema ao enviar o e-mail. Use o token manualmente se necessário."

# ==========================
# Validar token
# ==========================
def validar_token_reset(token):
    """
    Verifica se um token de redefinição de senha é válido e não expirou.
    Retorna (True, mensagem, email_usuario) ou (False, mensagem, None)
    """
    resp = supabase.table("usuarios").select("*").eq("reset_password_token", token).execute()
    if resp.error or not resp.data:
        logger.warning(f"Tentativa de validação com token inválido: {token}")
        return False, "Token de redefinição inválido ou já utilizado.", None

    usuario = resp.data[0]
    expires_at = usuario.get("reset_password_expires")
    if not expires_at or datetime.fromisoformat(expires_at) < datetime.now():
        logger.warning(f"Tentativa de validação com token expirado para {usuario['email']}")
        return False, "Token de redefinição expirado. Solicite um novo.", None

    logger.info(f"Token de reset válido para {usuario['email']}")
    return True, "Token válido.", usuario["email"]

# ==========================
# Redefinir senha com token
# ==========================
def redefinir_senha_com_token(token, nova_senha):
    """
    Redefine a senha de um usuário usando um token válido.
    """
    # 1. Validar token
    token_valido, msg, email_usuario = validar_token_reset(token)
    if not token_valido:
        return False, msg

    # 2. Criar hash da nova senha
    senha_hash = hash_password(nova_senha)

    # 3. Atualizar Supabase: nova senha e invalidar token
    update_resp = supabase.table("usuarios").update({
        "senha_hash": senha_hash,
        "reset_password_token": None,
        "reset_password_expires": None
    }).eq("email", email_usuario).execute()

    if update_resp.error:
        logger.error(f"Erro ao redefinir senha para {email_usuario}: {update_resp.error.message}")
        return False, "Erro interno ao redefinir senha."

    logger.info(f"Senha redefinida com sucesso para {email_usuario}")
    return True, "Senha redefinida com sucesso. Você já pode fazer login."
