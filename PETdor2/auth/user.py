# PETdor2/auth/user.py
"""
Módulo de usuários - autenticação e gerenciamento de contas.
"""
import logging
from datetime import datetime
from .security import hash_password, verify_password
from database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

def verificar_credenciais(email: str, senha: str) -> tuple[bool, dict]:
    """Verifica credenciais do usuário."""
    try:
        supabase = get_supabase()
        response = (
            supabase
            .from_("usuarios")
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
        logger.error(f"Erro ao verificar credenciais: {e}")
        return False, {"erro": str(e)}

def buscar_usuario_por_email(email: str) -> dict:
    """Busca um usuário pelo e-mail."""
    try:
        supabase = get_supabase()
        response = (
            supabase
            .from_("usuarios")
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )
        return response.data if response.data else None
    except Exception as e:
        logger.warning(f"Usuário não encontrado: {email}")
        return None

def cadastrar_usuario(nome: str, email: str, senha: str, tipo: str = "tutor", pais: str = "Brasil") -> tuple[bool, str]:
    """
    Cadastra um novo usuário.

    Args:
        nome: Nome completo do usuário
        email: E-mail do usuário
        senha: Senha do usuário
        tipo: Tipo de conta (tutor, veterinário, clínica)
        pais: País do usuário

    Returns:
        (True, mensagem) se sucesso, (False, mensagem_erro) caso contrário
    """
    try:
        supabase = get_supabase()

        # Verifica se já existe
        usuario_existente = buscar_usuario_por_email(email)
        if usuario_existente:
            return False, "❌ Este e-mail já está cadastrado."

        # Validações
        if len(senha) < 6:
            return False, "❌ Senha deve ter pelo menos 6 caracteres."

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
            "criado_em": datetime.utcnow().isoformat()
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

def atualizar_tipo_usuario(usuario_id: int, novo_tipo: str) -> bool:
    """Atualiza o tipo de um usuário."""
    try:
        supabase = get_supabase()
        supabase.from_("usuarios").update({"tipo": novo_tipo}).eq("id", usuario_id).execute()
        logger.info(f"✅ Tipo do usuário {usuario_id} atualizado para {novo_tipo}")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar tipo: {e}")
        return False

def atualizar_status_usuario(usuario_id: int, ativo: bool) -> bool:
    """Ativa ou desativa um usuário."""
    try:
        supabase = get_supabase()
        supabase.from_("usuarios").update({"ativo": ativo}).eq("id", usuario_id).execute()
        status = "ativado" if ativo else "desativado"
        logger.info(f"✅ Usuário {usuario_id} {status}")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        return False

__all__ = [
    "verificar_credenciais",
    "buscar_usuario_por_email",
    "cadastrar_usuario",
    "atualizar_tipo_usuario",
    "atualizar_status_usuario",
]
