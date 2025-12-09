# PetDor2/backend/auth/user.py
"""
Funções de usuário: cadastro, autenticação, busca e atualização.
Usa API genérica do supabase_client (supabase_table_*).
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from backend.database.supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)
from backend.auth.security import hash_password, verify_password
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"


def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo_usuario: str = "Tutor",
    pais: str = "Brasil",
    confirmar_senha: Optional[str] = None,
    is_admin: bool = False,
) -> Tuple[bool, str]:
    """
    Cadastra um novo usuário.
    Compatível tanto com chamadas que enviam confirmar_senha quanto com as que não enviam.
    """
    try:
        if not nome or not email or not senha:
            return False, "Preencha todos os campos obrigatórios."

        if confirmar_senha is not None and senha != confirmar_senha:
            return False, "As senhas não conferem."

        if not validar_email(email):
            return False, "E-mail inválido."

        if len(senha) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres."

        # Verifica existência
        ok, resp = supabase_table_select(TABELA_USUARIOS, "id", {"email": email.lower()}, single=False)
        if not ok:
            return False, f"Erro ao verificar usuário existente: {resp}"
        if resp:
            return False, "E-mail já cadastrado."

        senha_hash = hash_password(senha)
        agora = datetime.now().isoformat()

        dados = {
            "nome": nome.strip(),
            "email": email.lower(),
            "senha_hash": senha_hash,
            "tipo": tipo_usuario,
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": is_admin,
            "criado_em": agora,
            "atualizado_em": agora,
        }

        ok_ins, resultado = supabase_table_insert(TABELA_USUARIOS, dados)
        if not ok_ins:
            return False, f"Erro ao criar conta: {resultado}"

        logger.info(f"Usuário criado: {email}")
        return True, "Conta criada com sucesso. Verifique seu e-mail para confirmar."

    except Exception as e:
        logger.exception("Erro ao cadastrar usuário")
        return False, f"Erro interno ao criar conta: {e}"


def verificar_credenciais(email: str, senha: str) -> Tuple[bool, Any]:
    """
    Retorna (True, user_dict) se autenticado, ou (False, mensagem) em caso de falha.
    """
    try:
        if not email or not senha:
            return False, "E-mail e senha são obrigatórios."

        ok, usuario = supabase_table_select(TABELA_USUARIOS, "*", {"email": email.lower()}, single=True)
        if not ok:
            return False, "Erro ao buscar usuário."

        if not usuario:
            return False, "E-mail ou senha incorretos."

        senha_hash = usuario.get("senha_hash")
        if not senha_hash or not verify_password(senha, senha_hash):
            return False, "E-mail ou senha incorretos."

        if not usuario.get("ativo", True):
            return False, "Conta inativa. Contate o suporte."

        return True, usuario

    except Exception as e:
        logger.exception("Erro ao verificar credenciais")
        return False, f"Erro interno ao fazer login: {e}"


def buscar_usuario_por_email(email: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    try:
        ok, usuario = supabase_table_select(TABELA_USUARIOS, "*", {"email": email.lower()}, single=True)
        if not ok:
            return False, None
        return True, usuario
    except Exception as e:
        logger.exception("Erro ao buscar usuário por e-mail")
        return False, None


def buscar_usuario_por_id(user_id: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
    try:
        ok, usuario = supabase_table_select(TABELA_USUARIOS, "*", {"id": user_id}, single=True)
        if not ok:
            return False, None
        return True, usuario
    except Exception as e:
        logger.exception("Erro ao buscar usuário por ID")
        return False, None


def atualizar_usuario(user_id: int, **kwargs: Any) -> Tuple[bool, str]:
    allowed = {
        "nome", "email", "senha_hash", "tipo", "pais",
        "email_confirmado", "ativo", "is_admin", "email_confirm_token",
        "reset_password_token", "reset_password_expires"
    }
    dados_update = {k: v for k, v in kwargs.items() if k in allowed}
    if "email" in dados_update:
        dados_update["email"] = dados_update["email"].lower()
    dados_update["atualizado_em"] = datetime.now().isoformat()
    try:
        ok, resp = supabase_table_update(TABELA_USUARIOS, dados_update, {"id": user_id})
        if ok:
            return True, "Usuário atualizado com sucesso."
        else:
            return False, f"Erro ao atualizar usuário: {resp}"
    except Exception as e:
        logger.exception("Erro ao atualizar usuário")
        return False, f"Erro interno ao atualizar usuário: {e}"


def alterar_senha(user_id: int, nova_senha: str) -> Tuple[bool, str]:
    if len(nova_senha) < 8:
        return False, "Senha deve ter ao menos 8 caracteres."
    senha_hash = hash_password(nova_senha)
    return atualizar_usuario(user_id, senha_hash=senha_hash)


def deletar_usuario(user_id: int) -> Tuple[bool, str]:
    try:
        ok, resp = supabase_table_delete(TABELA_USUARIOS, {"id": user_id})
        if ok:
            return True, "Usuário deletado com sucesso."
        else:
            return False, f"Erro ao deletar usuário: {resp}"
    except Exception as e:
        logger.exception("Erro ao deletar usuário")
        return False, f"Erro interno ao deletar usuário: {e}"


# Compatibilidade
def atualizar_tipo_usuario(user_id: int, novo_tipo: str) -> Tuple[bool, str]:
    return atualizar_usuario(user_id, tipo=novo_tipo)


def atualizar_status_usuario(user_id: int, novo_status: bool) -> Tuple[bool, str]:
    return atualizar_usuario(user_id, ativo=novo_status)


def marcar_email_como_confirmado(email: str) -> Tuple[bool, str]:
    try:
        ok, _ = supabase_table_update(TABELA_USUARIOS, {
            "email_confirmado": True,
            "email_confirm_token": None,
            "atualizado_em": datetime.now().isoformat()
        }, {"email": email.lower()})
        if ok:
            return True, "E-mail confirmado com sucesso."
        return False, "Falha ao marcar e-mail como confirmado."
    except Exception as e:
        logger.exception("Erro ao marcar e-mail como confirmado")
        return False, f"Erro interno ao confirmar e-mail: {e}"
