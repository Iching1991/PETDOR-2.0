# PetDor2/backend/auth/user.py
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

# ============================================================
# 🔧 CORREÇÃO DOS IMPORTS (ABSOLUTOS a partir de 'backend' ou RELATIVOS)
# ============================================================
from backend.database.supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)
from .security import hash_password, verify_password
from backend.utils.validators import validar_email

# REMOVIDO: from .email_confirmation import enviar_email_confirmacao
# A função enviar_email_confirmacao será chamada de auth/email_confirmation.py
# e este módulo não precisa importá-la diretamente para evitar o ciclo.

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"

# =========================
# Cadastro de Usuário
# =========================
def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    confirmar_senha: str,
    tipo_usuario: str = "Tutor",
    pais: str = "Brasil",
    is_admin: bool = False,
) -> Tuple[bool, str]:
    """
    Cadastra um novo usuário no Supabase.
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        if not nome or not email or not senha or not confirmar_senha:
            return False, "Preencha todos os campos obrigatórios."
        if senha != confirmar_senha:
            return False, "As senhas não conferem."
        if not validar_email(email):
            return False, "E-mail inválido."
        if len(senha) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres."

        ok, usuarios_existentes = supabase_table_select(
            TABELA_USUARIOS,
            "id",
            {"email": email.lower()},
            single=False
        )
        if not ok:
            logger.error(f"Erro ao verificar usuário existente para {email}: {usuarios_existentes}")
            return False, f"Erro ao verificar usuário existente: {usuarios_existentes}"
        if usuarios_existentes:
            return False, "E-mail já cadastrado."

        senha_hash = hash_password(senha)

        dados_usuario = {
            "nome": nome.strip(),
            "email": email.lower(),
            "senha_hash": senha_hash,
            "tipo": tipo_usuario,
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": is_admin,
            "criado_em": datetime.now().isoformat(),
            "atualizado_em": datetime.now().isoformat()
        }

        ok_insert, resultado_insert = supabase_table_insert(TABELA_USUARIOS, dados_usuario)
        if not ok_insert or not resultado_insert:
            logger.error(f"Erro ao salvar usuário: {resultado_insert}")
            return False, f"Erro ao criar conta: {resultado_insert}"

        usuario_criado = resultado_insert[0]
        user_id = usuario_criado["id"]

        # A chamada para enviar_email_confirmacao será feita no módulo de cadastro (pages/cadastro.py)
        # ou no streamlit_app.py, após o sucesso do cadastro, para evitar o ciclo.
        # Ou, se preferir, podemos fazer um import local dentro de uma função, mas é mais limpo separar.

        logger.info(f"✅ Usuário {email} cadastrado com ID {user_id}")
        return True, "Conta criada com sucesso. Verifique seu e-mail para confirmar."

    except Exception as e:
        logger.exception("Erro inesperado ao cadastrar usuário")
        return False, f"Erro interno ao criar conta: {e}"

# =========================
# Verificação de Credenciais (Login)
# =========================
def verificar_credenciais(email: str, senha: str) -> Tuple[bool, str | Dict[str, Any]]:
    """
    Verifica as credenciais do usuário no Supabase.
    Retorna (True, user_data_dict) em caso de sucesso ou (False, mensagem de erro).
    """
    try:
        if not email or not senha:
            return False, "E-mail e senha são obrigatórios."

        ok, usuario_db = supabase_table_select(
            TABELA_USUARIOS,
            "*", # Seleciona todas as colunas para ter os dados completos do usuário
            {"email": email.lower()},
            single=True
        )

        if not ok:
            logger.error(f"Erro ao buscar usuário {email}: {usuario_db}")
            return False, "Erro ao tentar fazer login."

        if not usuario_db:
            return False, "E-mail ou senha incorretos."

        senha_hash_armazenado = usuario_db.get("senha_hash")
        if not senha_hash_armazenado or not verify_password(senha, senha_hash_armazenado):
            return False, "E-mail ou senha incorretos."

        if not usuario_db.get("ativo"):
            return False, "Sua conta está inativa. Entre em contato com o suporte."

        # Opcional: Se a confirmação de e-mail for obrigatória para login
        # if not usuario_db.get("email_confirmado"):
        #     return False, "Por favor, confirme seu e-mail antes de fazer login."

        logger.info(f"✅ Usuário {email} autenticado com sucesso.")
        return True, usuario_db # Retorna o dicionário completo do usuário

    except Exception as e:
        logger.exception(f"Erro inesperado ao verificar credenciais para {email}")
        return False, f"Erro interno ao fazer login: {e}"

# =========================
# Busca de Usuário
# =========================
def buscar_usuario_por_email(email: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Busca um usuário pelo e-mail no Supabase.
    Retorna (True, user_data_dict) ou (False, None).
    """
    try:
        ok, usuario = supabase_table_select(
            TABELA_USUARIOS,
            "*",
            {"email": email.lower()},
            single=True
        )
        if not ok:
            logger.error(f"Erro ao buscar usuário por e-mail {email}: {usuario}")
            return False, None
        return True, usuario
    except Exception as e:
        logger.exception(f"Erro ao buscar usuário por e-mail {email}")
        return False, None

def buscar_usuario_por_id(user_id: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Busca um usuário pelo ID no Supabase.
    Retorna (True, user_data_dict) ou (False, None).
    """
    try:
        ok, usuario = supabase_table_select(
            TABELA_USUARIOS,
            "*",
            {"id": user_id},
            single=True
        )
        if not ok:
            logger.error(f"Erro ao buscar usuário por ID {user_id}: {usuario}")
            return False, None
        return True, usuario
    except Exception as e:
        logger.exception(f"Erro ao buscar usuário por ID {user_id}")
        return False, None

# =========================
# Atualização de Usuário
# =========================
def atualizar_usuario(user_id: int, **kwargs: Any) -> Tuple[bool, str]:
    """
    Atualiza dados de um usuário no Supabase.
    Ex: atualizar_usuario(1, nome="Novo Nome", tipo="Admin")
    """
    try:
        dados_update = {k: v for k, v in kwargs.items() if k in [
            "nome", "email", "senha_hash", "tipo", "pais",
            "email_confirmado", "ativo", "is_admin", "email_confirm_token",
            "reset_password_token", "reset_password_expires_at"
        ]}
        dados_update["atualizado_em"] = datetime.now().isoformat()

        if "email" in dados_update:
            dados_update["email"] = dados_update["email"].lower() # Garante minúsculas

        ok, resultado_update = supabase_table_update(
            TABELA_USUARIOS,
            dados_update,
            {"id": user_id}
        )
        if ok:
            logger.info(f"✅ Usuário {user_id} atualizado com sucesso: {kwargs}")
            return True, "Usuário atualizado com sucesso."
        else:
            logger.error(f"❌ Falha ao atualizar usuário {user_id}: {resultado_update}")
            return False, f"Erro ao atualizar usuário: {resultado_update}"
    except Exception as e:
        logger.exception(f"Erro ao atualizar usuário {user_id} no Supabase")
        return False, f"Erro interno ao atualizar usuário: {e}"

def alterar_senha(user_id: int, nova_senha: str) -> Tuple[bool, str]:
    """
    Altera a senha de um usuário.
    """
    try:
        if len(nova_senha) < 8:
            return False, "A nova senha deve ter pelo menos 8 caracteres."
        senha_hash = hash_password(nova_senha)
        return atualizar_usuario(user_id, senha_hash=senha_hash)
    except Exception as e:
        logger.exception(f"Erro ao alterar senha para usuário {user_id}")
        return False, f"Erro interno ao alterar senha: {e}"

# =========================
# Deleção de Usuário
# =========================
def deletar_usuario(user_id: int) -> Tuple[bool, str]:
    """
    Deleta um usuário do Supabase.
    """
    try:
        ok, resultado_delete = supabase_table_delete(
            TABELA_USUARIOS,
            {"id": user_id}
        )
        if ok:
            logger.info(f"✅ Usuário {user_id} deletado com sucesso.")
            return True, "Usuário deletado com sucesso."
        else:
            logger.error(f"❌ Falha ao deletar usuário {user_id}: {resultado_delete}")
            return False, f"Erro ao deletar usuário: {resultado_delete}"
    except Exception as e:
        logger.exception(f"Erro ao deletar usuário {user_id} no Supabase")
        return False, f"Erro interno ao deletar usuário: {e}"

# =========================
# Funções de compatibilidade (para uso em outros módulos)
# =========================
def atualizar_tipo_usuario(user_id: int, novo_tipo: str) -> Tuple[bool, str]:
    """Atualiza o tipo de usuário no Supabase."""
    return atualizar_usuario(user_id, tipo=novo_tipo)

def atualizar_status_usuario(user_id: int, novo_status: bool) -> Tuple[bool, str]:
    """Atualiza o status (ativo/inativo) do usuário no Supabase."""
    return atualizar_usuario(user_id, ativo=novo_status)

def marcar_email_como_confirmado(email: str) -> Tuple[bool, str]:
    """
    Marca e-mail como confirmado no Supabase e remove o token de confirmação.
    Esta função é chamada por auth.email_confirmation.confirmar_email_com_token.
    """
    try:
        dados_update = {
            "email_confirmado": True,
            "email_confirm_token": None,  # Remove o token após a confirmação
            "atualizado_em": datetime.now().isoformat()
        }
        ok, _ = supabase_table_update(TABELA_USUARIOS, dados_update, {"email": email.lower()})
        if ok:
            logger.info(f"✅ E-mail {email} marcado como confirmado.")
            return True, "E-mail confirmado com sucesso."
        else:
            return False, "Falha ao marcar e-mail como confirmado."
    except Exception as e:
        logger.exception(f"Erro ao marcar e-mail {email} como confirmado")
        return False, f"Erro interno ao confirmar e-mail: {e}"

