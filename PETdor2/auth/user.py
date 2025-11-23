# PETdor2/auth/user.py
import logging
from typing import Optional, Tuple
from auth.security import hash_password, verify_password  # supondo que você tenha funções de hash

logger = logging.getLogger(__name__)

# -------------------------
# FUNÇÕES DE USUÁRIO
# -------------------------

def cadastrar_usuario(nome: str, email: str, senha: str, tipo_usuario: str, pais: str) -> Tuple[bool, str]:
    """
    Cadastra um novo usuário no Supabase.
    Retorna (True, mensagem) ou (False, mensagem de erro)
    """
    try:
        from database.supabase_client import supabase  # import local
        senha_hash = hash_password(senha)
        resp = supabase.table("usuarios").insert({
            "nome": nome,
            "email": email,
            "senha_hash": senha_hash,
            "tipo_usuario": tipo_usuario,
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "data_cadastro": None
        }).execute()

        if resp.error:
            logger.error(f"Erro ao cadastrar usuário {email}: {resp.error.message}")
            return False, f"Erro ao cadastrar usuário: {resp.error.message}"

        return True, "Usuário cadastrado com sucesso! Confirme seu e-mail."
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário {email}: {e}", exc_info=True)
        return False, str(e)


def verificar_credenciais(email: str, senha: str) -> Tuple[bool, Optional[dict]]:
    """
    Verifica se o e-mail e senha correspondem a um usuário registrado.
    Retorna (True, dict_usuario) ou (False, mensagem)
    """
    try:
        from database.supabase_client import supabase  # import local
        resp = supabase.table("usuarios").select("*").eq("email", email).execute()
        if not resp.data:
            return False, "Usuário não encontrado."
        user = resp.data[0]
        if not verify_password(senha, user["senha_hash"]):
            return False, "Senha incorreta."
        return True, user
    except Exception as e:
        logger.error(f"Erro ao verificar credenciais {email}: {e}", exc_info=True)
        return False, str(e)


def buscar_usuario_por_email(email: str) -> Optional[dict]:
    """
    Retorna o dicionário do usuário ou None se não encontrado
    """
    try:
        from database.supabase_client import supabase  # import local
        resp = supabase.table("usuarios").select("*").eq("email", email).execute()
        return resp.data[0] if resp.data else None
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por email {email}: {e}", exc_info=True)
        return None


def confirmar_email(token: str) -> Tuple[bool, str]:
    """
    Confirma o e-mail de um usuário usando o token enviado por e-mail.
    """
    try:
        from database.supabase_client import supabase  # import local
        resp = supabase.table("usuarios").update({"email_confirmado": True}).eq("email_confirm_token", token).execute()
        if resp.error:
            logger.error(f"Erro ao confirmar e-mail com token {token}: {resp.error.message}")
            return False, f"Erro ao confirmar e-mail: {resp.error.message}"
        return True, "E-mail confirmado com sucesso!"
    except Exception as e:
        logger.error(f"Erro ao confirmar e-mail com token {token}: {e}", exc_info=True)
        return False, str(e)
