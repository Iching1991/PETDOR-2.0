# PetDor2/auth/user.py
"""
Gerenciamento de usuários: cadastro, autenticação, atualização, confirmação de e-mail.
Migrado de SQLite para Supabase.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Importações do novo sistema Supabase
from database.supabase_client import supabase_table_select, supabase_table_insert, supabase_table_update
from auth.security import gerar_hash_senha, verificar_senha
from utils.validators import validar_email, validar_senha
from utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"

# -------------------------
# Cadastrar usuário (migrado de SQLite para Supabase)
# -------------------------
def cadastrar_usuario(nome: str, email: str, senha: str, confirmar: str,
                      tipo_usuario: str = "Tutor", pais: str = "Brasil") -> Tuple[bool, str]:
    """
    Cadastra usuário no Supabase (substitui INSERT SQL).
    """
    try:
        nome = nome.strip()
        email = email.strip().lower()

        if not nome or not email or not senha:
            return False, "Preencha todos os campos obrigatórios."

        if senha != confirmar:
            return False, "As senhas não conferem."

        if not validar_email(email):
            return False, "E-mail inválido."

        # Validação de senha (opcional — se quiser regras estritas)
        # if not validar_senha(senha):
        #     return False, "Senha não atende os requisitos de segurança."

        # Verifica duplicado no Supabase (substitui SELECT SQL)
        ok, usuarios = supabase_table_select(
            TABELA_USUARIOS, 
            "id", 
            {"email": email}, 
            single=False
        )
        if not ok:
            return False, f"Erro ao verificar usuário existente: {usuarios}"
        if usuarios:
            return False, "E-mail já cadastrado."

        # Gera hash da senha
        senha_hash = gerar_hash_senha(senha)

        # Gera token de confirmação (UUID)
        token_confirmacao = str(uuid.uuid4())

        # Insere usuário no Supabase (substitui INSERT SQL)
        dados_usuario = {
            "nome": nome,
            "email": email,
            "senha_hash": senha_hash,
            "tipo_usuario": tipo_usuario,
            "pais": pais,
            "email_confirm_token": token_confirmacao,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": False,
            "criado_em": datetime.now().isoformat(),
            "atualizado_em": datetime.now().isoformat()
        }

        ok_insert, resultado_insert = supabase_table_insert(TABELA_USUARIOS, dados_usuario)
        if not ok_insert or not resultado_insert:
            return False, f"Erro ao salvar usuário: {resultado_insert}"

        usuario_criado = resultado_insert[0]
        user_id = usuario_criado["id"]

        # Tenta enviar e-mail de confirmação (não crítico)
        try:
            enviar_email_confirmacao(email, nome, token_confirmacao)
        except Exception as e:
            logger.warning(f"Falha ao enviar email de confirmação para {email}: {e}")

        logger.info(f"✅ Usuário {email} cadastrado com ID {user_id} no Supabase")
        return True, "Conta criada com sucesso. Verifique seu e-mail para confirmar."

    except Exception as e:
        logger.exception("Erro ao cadastrar usuário no Supabase")
        return False, f"Erro ao criar conta: {e}"

# -------------------------
# Autenticar usuário (migrado de SQLite para Supabase)
# -------------------------
def autenticar_usuario(email: str, senha: str) -> Tuple[bool, str, Optional[int]]:
    """
    Autentica usuário no Supabase (substitui SELECT + bcrypt.checkpw).
    """
    try:
        if not email or not senha:
            return False, "E-mail e senha são obrigatórios.", None

        email = email.strip().lower()

        # Busca usuário no Supabase (substitui SELECT SQL)
        ok, usuario = supabase_table_select(
            TABELA_USUARIOS, 
            "id, senha_hash, ativo, email_confirmado", 
            {"email": email}, 
            single=True
        )
        if not ok:
            return False, f"Erro ao buscar usuário: {usuario}", None

        if not usuario:
            return False, "Usuário não encontrado.", None

        user_id = usuario["id"]
        senha_hash = usuario["senha_hash"]
        ativo = usuario["ativo"]
        email_confirmado = usuario["email_confirmado"]

        if not ativo:
            return False, "Conta desativada.", None

        # Opcional: exigir confirmação de e-mail
        # if not email_confirmado:
        #     return False, "Confirme seu e-mail antes de entrar.", None

        # Verifica senha (substitui bcrypt.checkpw)
        if verificar_senha(senha, senha_hash):
            logger.info(f"✅ Usuário {email} autenticado com sucesso (ID: {user_id})")
            return True, "Login efetuado com sucesso.", user_id
        else:
            logger.warning(f"❌ Falha na autenticação para {email}")
            return False, "E-mail ou senha incorretos.", None

    except Exception as e:
        logger.exception("Erro na autenticação no Supabase")
        return False, "Erro ao autenticar.", None

# -------------------------
# Buscar usuário (migrado de SQLite para Supabase)
# -------------------------
def buscar_usuario_por_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Busca usuário por ID no Supabase (substitui SELECT SQL).
    """
    try:
        ok, usuario = supabase_table_select(
            TABELA_USUARIOS, 
            "id, nome, email, tipo_usuario, pais, email_confirmado, ativo", 
            {"id": user_id}, 
            single=True
        )
        if not ok or not usuario:
            return None

        return {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "tipo_usuario": usuario["tipo_usuario"],
            "pais": usuario["pais"],
            "email_confirmado": bool(usuario["email_confirmado"]),
            "ativo": bool(usuario["ativo"])
        }
    except Exception as e:
        logger.exception("Erro ao buscar usuário por id no Supabase")
        return None

def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário por email no Supabase (substitui SELECT SQL).
    """
    try:
        email = email.strip().lower()
        ok, usuario = supabase_table_select(
            TABELA_USUARIOS, 
            "id, nome, email, tipo_usuario, pais, email_confirmado, ativo", 
            {"email": email}, 
            single=True
        )
        if not ok or not usuario:
            return None

        return {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "tipo_usuario": usuario["tipo_usuario"],
            "pais": usuario["pais"],
            "email_confirmado": bool(usuario["email_confirmado"]),
            "ativo": bool(usuario["ativo"])
        }
    except Exception as e:
        logger.exception("Erro ao buscar usuário por email no Supabase")
        return None

# -------------------------
# Atualizar usuário (migrado de SQLite para Supabase)
# -------------------------
def atualizar_usuario(user_id: int, nome: str = None, email: str = None, 
                     tipo_usuario: str = None, pais: str = None) -> bool:
    """
    Atualiza usuário no Supabase (substitui UPDATE SQL).
    """
    try:
        # Prepara dados para atualização
        dados_update = {}
        if nome:
            dados_update["nome"] = nome.strip()
        if email:
            dados_update["email"] = email.strip().lower()
        if tipo_usuario:
            dados_update["tipo_usuario"] = tipo_usuario
        if pais:
            dados_update["pais"] = pais
        dados_update["atualizado_em"] = datetime.now().format()

        if not dados_update:
            logger.warning(f"Nenhum campo para atualizar no usuário {user_id}")
            return True

        # Atualiza no Supabase (substitui UPDATE SQL)
        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS, 
            dados_update, 
            {"id": user_id}
        )

        if ok_update:
            logger.info(f"✅ Usuário {user_id} atualizado no Supabase")
            return True
        else:
            logger.error(f"❌ Falha ao atualizar usuário {user_id}: {resultado_update}")
            return False

    except Exception as e:
        logger.exception("Erro ao atualizar usuário no Supabase")
        return False

# -------------------------
# Alterar senha (migrado de SQLite para Supabase)
# -------------------------
def alterar_senha(user_id: int, nova_senha: str) -> Tuple[bool, str]:
    """
    Altera senha no Supabase (substitui UPDATE SQL + bcrypt).
    """
    try:
        senha_hash = gerar_hash_senha(nova_senha)

        dados_update = {
            "senha_hash": senha_hash,
            "atualizado_em": datetime.now().isoformat()
        }

        # Atualiza no Supabase
        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS, 
            dados_update, 
            {"id": user_id}
        )

        if ok_update:
            logger.info(f"✅ Senha alterada para usuário {user_id}")
            return True, "Senha alterada com sucesso."
        else:
            return False, f"Erro ao alterar senha: {resultado_update}"

    except Exception as e:
        logger.exception("Erro ao alterar senha no Supabase")
        return False, f"Erro ao alterar senha: {e}"

# -------------------------
# Deletar / desativar usuário (migrado de SQLite para Supabase)
# -------------------------
def deletar_usuario(user_id: int) -> bool:
    """
    Desativa usuário no Supabase (substitui UPDATE SQL).
    """
    try:
        dados_update = {
            "ativo": False,
            "atualizado_em": datetime.now().isoformat()
        }

        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS, 
            dados_update, 
            {"id": user_id}
        )

        if ok_update:
            logger.info(f"✅ Usuário {user_id} desativado no Supabase")
            return True
        else:
            logger.error(f"❌ Falha ao desativar usuário {user_id}: {resultado_update}")
            return False

    except Exception as e:
        logger.exception("Erro ao desativar usuário no Supabase")
        return False

# -------------------------
# Token de confirmação de e-mail (migrado de SQLite para Supabase)
# -------------------------
def gerar_token_confirmacao_para_usuario(user_id: int) -> Optional[str]:
    """
    Gera e salva token de confirmação no Supabase (substitui UPDATE SQL).
    """
    try:
        token = str(uuid.uuid4())

        dados_update = {
            "email_confirm_token": token,
            "atualizado_em": datetime.now().isoformat()
        }

        ok_update, _ = supabase_table_update(
            TABELA_USUARIOS, 
            dados_update, 
            {"id": user_id}
        )

        if ok_update:
            logger.info(f"✅ Token de confirmação gerado para usuário {user_id}")
            return token
        else:
            logger.error(f"❌ Falha ao gerar token para usuário {user_id}")
            return None

    except Exception as e:
        logger.exception("Erro ao gerar token de confirmação no Supabase")
        return None

def confirmar_email(token: str) -> bool:
    """
    Confirma e-mail no Supabase (substitui UPDATE + DELETE SQL).
    """
    try:
        # Busca usuário pelo token
        ok, usuario = supabase_table_select(
            TABELA_USUARIOS, 
            "id", 
            {"email_confirm_token": token}, 
            single=True
        )
        if not ok or not usuario:
            logger.warning(f"Token de confirmação inválido: {token}")
            return False

        user_id = usuario["id"]

        # Atualiza status de confirmação
        dados_update = {
            "email_confirmado": True,
            "email_confirm_token": None,  # Remove o token
            "atualizado_em": datetime.now().isoformat()
        }

        ok_update, _ = supabase_table_update(
            TABELA_USUARIOS, 
            dados_update, 
            {"id": user_id}
        )

        if ok_update:
            logger.info(f"✅ E-mail confirmado para usuário {user_id}")
            return True
        else:
            logger.error(f"❌ Falha ao confirmar e-mail para usuário {user_id}")
            return False

    except Exception as e:
        logger.exception("Erro ao confirmar e-mail no Supabase")
        return False

# Funções adicionais para compatibilidade com o app
def atualizar_tipo_usuario(user_id: int, novo_tipo: str) -> bool:
    """Atualiza tipo de usuário no Supabase."""
    return atualizar_usuario(user_id, tipo_usuario=novo_tipo)

def atualizar_status_usuario(user_id: int, novo_status: bool) -> bool:
    """Atualiza status (ativo/inativo) no Supabase."""
    dados_update = {
        "ativo": novo_status,
        "atualizado_em": datetime.now().isoformat()
    }
    ok, _ = supabase_table_update(TABELA_USUARIOS, dados_update, {"id": user_id})
    return ok

def marcar_email_como_confirmado(email: str) -> bool:
    """Marca e-mail como confirmado no Supabase."""
    dados_update = {
        "email_confirmado": True,
        "atualizado_em": datetime.now().isoformat()
    }
    ok, _ = supabase_table_update(TABELA_USUARIOS, dados_update, {"email": email.lower()})
    return ok
