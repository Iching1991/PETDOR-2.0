# PETdor2/auth/user.py
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# -------------------------
# FUNÇÕES DE USUÁRIO
# -------------------------

def cadastrar_usuario(nome: str, email: str, senha: str, tipo_usuario: str, pais: str) -> Tuple[bool, str]:
    try:
        from database.supabase_client import supabase  # import local
        # Aqui você colocaria a lógica de hash da senha e insert no supabase
        senha_hash = senha  # substituir por hash real
        resp = supabase.table("usuarios").insert({
            "nome": nome,
            "email": email,
            "senha_hash": senha_hash,
            "tipo_usuario": tipo_usuario,
            "pais": pais
        }).execute()
        if resp.error:
            return False, f"Erro ao cadastrar usuário: {resp.error}"
        return True, "Usuário cadastrado com sucesso! Confirme seu e-mail."
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário {email}: {e}")
        return False, str(e)

def verificar_credenciais(email: str, senha: str) -> Tuple[bool, Optional[dict]]:
    try:
        from database.supabase_client import supabase  # import local
        resp = supabase.table("usuarios").select("*").eq("email", email).execute()
        if not resp.data:
            return False, "Usuário não encontrado."
        user = resp.data[0]
        if senha != user["senha_hash"]:  # substituir por check_hash real
            return False, "Senha incorreta."
        return True, user
    except Exception as e:
        logger.error(f"Erro ao verificar credenciais {email}: {e}")
        return False, str(e)

def buscar_usuario_por_email(email: str) -> Optional[dict]:
    try:
        from database.supabase_client import supabase  # import local
        resp = supabase.table("usuarios").select("*").eq("email", email).execute()
        return resp.data[0] if resp.data else None
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por email {email}: {e}")
        return None

def confirmar_email(token: str) -> Tuple[bool, str]:
    try:
        from database.supabase_client import supabase  # import local
        # lógica de confirmação pelo token
        resp = supabase.table("usuarios").update({"email_confirmado": True}).eq("email_confirm_token", token).execute()
        if resp.error:
            return False, f"Erro ao confirmar e-mail: {resp.error}"
        return True, "E-mail confirmado com sucesso!"
    except Exception as e:
        logger.error(f"Erro ao confirmar e-mail com token {token}: {e}")
        return False, str(e)
