# PETdor2/auth/user.py
"""
Módulo de usuário - autenticação e gerenciamento de contas.
"""
import logging
from .security import hash_password, verify_password
from database.supabase_client import supabase

logger = logging.getLogger(__name__)

def verificar_credenciais(email: str, senha: str) -> tuple[bool, str | dict]:
    """
    Verifica as credenciais do usuário.

    Returns:
        (sucesso, resultado) onde resultado é mensagem de erro ou dados do usuário
    """
    try:
        # Busca o usuário no Supabase
        response = (
            supabase
            .from_("usuarios")
            .select("*")
            .eq("email", email)
            .execute()
        )

        usuarios = getattr(response, "data", None) or (response.get("data") if isinstance(response, dict) else None)

        if not usuarios or len(usuarios) == 0:
            return False, "❌ E-mail ou senha incorretos."

        usuario = usuarios[0]

        # Verifica a senha
        if not verify_password(senha, usuario["senha_hash"]):
            return False, "❌ E-mail ou senha incorretos."

        # Verifica se o e-mail está confirmado
        if not usuario.get("email_confirmado", False):
            return False, "⚠️ Por favor, confirme seu e-mail antes de fazer login."

        logger.info(f"✅ Usuário {email} logado com sucesso")
        return True, usuario

    except Exception as e:
        logger.error(f"Erro ao verificar credenciais: {e}")
        return False, f"❌ Erro ao fazer login: {e}"

def buscar_usuario_por_email(email: str) -> dict | None:
    """Busca um usuário pelo e-mail."""
    try:
        response = (
            supabase
            .from_("usuarios")
            .select("*")
            .eq("email", email)
            .execute()
        )

        usuarios = getattr(response, "data", None) or (response.get("data") if isinstance(response, dict) else None)
        return usuarios[0] if usuarios else None

    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return None

def cadastrar_usuario(nome: str, email: str, senha: str, tipo_usuario: str = "tutor") -> tuple[bool, str]:
    """
    Cadastra um novo usuário.

    Args:
        nome: Nome completo
        email: E-mail
        senha: Senha em texto plano
        tipo_usuario: "tutor", "clinica" ou "veterinario"

    Returns:
        (sucesso, mensagem)
    """
    try:
        # Verifica se o e-mail já existe
        usuario_existente = buscar_usuario_por_email(email)
        if usuario_existente:
            return False, "❌ Este e-mail já está cadastrado."

        # Hash da senha
        senha_hash = hash_password(senha)

        # Insere o novo usuário
        payload = {
            "nome": nome,
            "email": email,
            "senha_hash": senha_hash,
            "tipo_usuario": tipo_usuario,
            "email_confirmado": False,
            "criado_em": datetime.utcnow().isoformat()
        }

        response = supabase.table("usuarios").insert(payload).execute()
        logger.info(f"✅ Usuário {email} cadastrado com sucesso")
        return True, "✅ Cadastro realizado com sucesso! Verifique seu e-mail."

    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}")
        return False, f"❌ Erro ao cadastrar: {e}"

__all__ = ["verificar_credenciais", "buscar_usuario_por_email", "cadastrar_usuario"]
