# PETdor2/backend/auth/user.py
"""
Módulo de usuários - autenticação e gerenciamento de contas.
"""
import logging
from datetime import datetime

from .security import hash_password, verify_password
from ..database.supabase_client import get_supabase  # import relativo corrigido

logger = logging.getLogger(__name__)

# ==========================================================
# LOGIN / AUTENTICAÇÃO
# ==========================================================
def verificar_credenciais(email: str, senha: str) -> tuple[bool, dict]:
    """Verifica credenciais do usuário."""
    try:
        supabase = get_supabase()
        response = (
            supabase.from_("usuarios")
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )

        usuario = response.data
        if not usuario:
            return False, {"erro": "Usuário não encontrado"}

        if not verify_password(senha, usuario.get("senha_hash", "")):
            return False, {"erro": "Senha incorreta"}

        logger.info(f"✅ Login bem-sucedido para {email}")
        return True, usuario

    except Exception as e:
        logger.error(f"Erro ao verificar credenciais: {e}", exc_info=True)
        return False, {"erro": str(e)}

# ==========================================================
# BUSCA DE USUÁRIO
# ==========================================================
def buscar_usuario_por_email(email: str) -> dict | None:
    """Busca um usuário pelo e-mail."""
    try:
        supabase = get_supabase()
        response = (
            supabase.from_("usuarios")
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )
        return response.data if response.data else None

    except Exception:
        logger.warning(f"Usuário não encontrado: {email}")
        return None

# ==========================================================
# CADASTRO
# ==========================================================
def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str = "tutor",
    pais: str = "Brasil"
) -> tuple[bool, str]:
    """Cadastra um novo usuário no sistema."""
    try:
        supabase = get_supabase()

        # Verifica se já existe
        if buscar_usuario_por_email(email):
            return False, "❌ Este e-mail já está cadastrado."

        # Valida senha
        if len(senha) < 6:
            return False, "❌ A senha deve ter pelo menos 6 caracteres."

        senha_hash = hash_password(senha)
        payload = {
            "nome": nome,
            "email": email.lower(),
            "senha_hash": senha_hash,
            "tipo": tipo,
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": False,
            "criado_em": datetime.utcnow().isoformat(),
        }

        response = supabase.from_("usuarios").insert(payload).execute()

        if not response.data:
            logger.error(f"Erro ao inserir usuário: {email}")
            return False, "❌ Erro ao cadastrar. Tente novamente."

        logger.info(f"✅ Usuário {email} cadastrado com sucesso")
        return True, "✅ Cadastro realizado com sucesso! Verifique seu e-mail."

    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}", exc_info=True)
        return False, f"❌ Erro ao cadastrar: {str(e)}"

# ==========================================================
# REDEFINIR SENHA
# ==========================================================
def redefinir_senha(usuario_id: int, senha_atual: str, nova_senha: str) -> tuple[bool, str]:
    """Redefine a senha do usuário após validar a senha atual."""
    try:
        supabase = get_supabase()

        response = (
            supabase.from_("usuarios")
            .select("senha_hash")
            .eq("id", usuario_id)
            .single()
            .execute()
        )
        usuario = response.data

        if not usuario:
            return False, "❌ Usuário não encontrado."

        if not verify_password(senha_atual, usuario.get("senha_hash", "")):
            return False, "❌ Senha atual incorreta."

        if len(nova_senha) < 8:
            return False, "❌ A nova senha deve ter pelo menos 8 caracteres."

        nova_senha_hash = hash_password(nova_senha)
        supabase.from_("usuarios").update({"senha_hash": nova_senha_hash}).eq("id", usuario_id).execute()

        logger.info(f"🔐 Senha redefinida para usuário {usuario_id}")
        return True, "✅ Senha alterada com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}", exc_info=True)
        return False, f"❌ Erro ao redefinir senha: {str(e)}"

# ==========================================================
# ALTERAÇÕES DE PERMISSÃO E STATUS
# ==========================================================
def atualizar_tipo_usuario(usuario_id: int, novo_tipo: str) -> bool:
    """Atualiza o tipo de usuário (tutor, veterinário, admin, etc.)."""
    try:
        supabase = get_supabase()
        supabase.from_("usuarios").update({"tipo": novo_tipo}).eq("id", usuario_id).execute()
        logger.info(f"🔄 Tipo atualizado para {usuario_id}: {novo_tipo}")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar tipo: {e}", exc_info=True)
        return False

def atualizar_status_usuario(usuario_id: int, ativo: bool) -> bool:
    """Ativa ou desativa um usuário."""
    try:
        supabase = get_supabase()
        supabase.from_("usuarios").update({"ativo": ativo}).eq("id", usuario_id).execute()

        status = "ativado" if ativo else "desativado"
        logger.info(f"⚡ Usuário {usuario_id} {status}")
        return True

    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}", exc_info=True)
        return False

# ==========================================================
# EXPORTS
# ==========================================================
__all__ = [
    "verificar_credenciais",
    "buscar_usuario_por_email",
    "cadastrar_usuario",
    "redefinir_senha",
    "atualizar_tipo_usuario",
    "atualizar_status_usuario",
]
