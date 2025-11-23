# PETdor2/auth/user.py
import hashlib
import os
import logging
import uuid
from database.models import buscar_usuario_por_email
from database.supabase_client import supabase
from utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)

# ==========================
# Funções auxiliares
# ==========================
def hash_senha(senha: str) -> str:
    """Gera hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode()).hexdigest()


def generate_email_token() -> str:
    """Gera um token UUID aleatório para confirmação de e-mail."""
    return str(uuid.uuid4())


# ==========================
# Cadastro de usuário
# ==========================
def cadastrar_usuario(nome: str, email: str, senha: str, tipo_usuario="Tutor", pais="Brasil") -> tuple[bool, str]:
    # 1. Verificar se já existe usuário
    usuario_existente = buscar_usuario_por_email(email)
    if usuario_existente:
        return False, "Erro ao cadastrar usuário: Este e-mail já está em uso."

    # 2. Criar hash da senha e token de confirmação
    senha_hash = hash_senha(senha)
    email_token = generate_email_token()

    # 3. Inserir no Supabase
    resp = supabase.table("usuarios").insert({
        "nome": nome,
        "email": email.lower(),
        "senha_hash": senha_hash,
        "tipo_usuario": tipo_usuario,
        "pais": pais,
        "email_confirm_token": email_token,
        "email_confirmado": False,
        "ativo": True
    }).execute()

    if resp.error:
        logger.error(f"Erro ao cadastrar usuário {email}: {resp.error.message}")
        return False, f"Erro ao cadastrar usuário: {resp.error.message}"

    # 4. Enviar e-mail de confirmação
    try:
        app_url = os.getenv("STREAMLIT_APP_URL", "http://localhost:8501")
        confirm_link = f"{app_url}?action=confirm_email&token={email_token}"
        email_enviado, msg_email = enviar_email_confirmacao(email, nome, confirm_link)
        if email_enviado:
            logger.info(f"E-mail de confirmação enviado para {email}.")
            return True, "Cadastro realizado com sucesso! Verifique seu e-mail para confirmar sua conta."
        else:
            logger.warning(f"Falha ao enviar e-mail de confirmação: {msg_email}")
            return True, "Cadastro realizado com sucesso, mas falha ao enviar o e-mail de confirmação."
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de confirmação para {email}: {e}", exc_info=True)
        return True, "Cadastro realizado com sucesso, mas falha ao enviar o e-mail de confirmação."


# ==========================
# Verificação de credenciais (login)
# ==========================
def verificar_credenciais(email: str, senha: str) -> tuple[bool, dict | str]:
    usuario = buscar_usuario_por_email(email)
    if not usuario:
        return False, "Usuário não encontrado."
    if usuario.senha_hash != hash_senha(senha):
        return False, "Senha incorreta."
    if not usuario.email_confirmado:
        return False, "Sua conta ainda não foi confirmada. Verifique seu e-mail."
    if not usuario.ativo:
        return False, "Sua conta está inativa. Contate o suporte."

    return True, {
        "id": usuario.id,
        "email": usuario.email,
        "nome": usuario.nome,
        "tipo_usuario": usuario.tipo_usuario
    }


# ==========================
# Confirmação de e-mail
# ==========================
def confirmar_email(token: str) -> tuple[bool, str]:
    # 1. Buscar usuário pelo token
    resp = supabase.table("usuarios").select("*").eq("email_confirm_token", token).execute()
    if resp.error or not resp.data:
        return False, "Token de confirmação inválido ou expirado."

    usuario = resp.data[0]

    # 2. Atualizar status de confirmação
    update_resp = supabase.table("usuarios").update({
        "email_confirmado": True,
        "email_confirm_token": None
    }).eq("id", usuario["id"]).execute()

    if update_resp.error:
        logger.error(f"Erro ao confirmar e-mail para {usuario['email']}: {update_resp.error.message}")
        return False, "Erro interno ao confirmar e-mail."

    logger.info(f"E-mail {usuario['email']} confirmado com sucesso.")
    return True, "Seu e-mail foi confirmado com sucesso! Você já pode fazer login."
