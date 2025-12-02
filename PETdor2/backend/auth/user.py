# PetDor2/backend/auth/user.py
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

# ============================================================
# 🔧 CORREÇÃO DOS IMPORTS (ABSOLUTOS a partir de 'backend' ou RELATIVOS)
# ============================================================
# Importações do novo sistema Supabase (absolutas a partir de 'backend')
from database.supabase_client import ( # Corrigido: database.supabase_client
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)
# Importações relativas dentro do pacote 'auth'
from .security import hash_password, verify_password # Corrigido: .security
from .email_confirmation import enviar_email_confirmacao # Corrigido: .email_confirmation

# Importações de 'utils' (absolutas a partir de 'backend')
from utils.validators import validar_email # Corrigido: utils.validators

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
    tipo_usuario: str = "Tutor",  # Padrão para "Tutor"
    pais: str = "Brasil",
    is_admin: bool = False, # Define se o usuário é admin no cadastro
) -> Tuple[bool, str]:
    """
    Cadastra um novo usuário no Supabase.
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        # 1. Validações básicas
        if not nome or not email or not senha or not confirmar_senha:
            return False, "Preencha todos os campos obrigatórios."
        if senha != confirmar_senha:
            return False, "As senhas não conferem."
        if not validar_email(email):
            return False, "E-mail inválido."
        if len(senha) < 8: # Adiciona validação de tamanho mínimo da senha
            return False, "A senha deve ter pelo menos 8 caracteres."

        # 2. Verifica se o e-mail já está cadastrado no Supabase
        ok, usuarios_existentes = supabase_table_select(
            TABELA_USUARIOS,
            "id",
            {"email": email.lower()}, # Garante que a busca é case-insensitive
            single=False
        )
        if not ok:
            logger.error(f"Erro ao verificar usuário existente para {email}: {usuarios_existentes}")
            return False, f"Erro ao verificar usuário existente: {usuarios_existentes}"
        if usuarios_existentes:
            return False, "E-mail já cadastrado."

        # 3. Gera hash da senha
        senha_hash = hash_password(senha)

        # 4. Insere usuário no Supabase
        dados_usuario = {
            "nome": nome,
            "email": email.lower(), # Salva e-mail em minúsculas
            "senha_hash": senha_hash,
            "tipo": tipo_usuario, # Coluna 'tipo' no Supabase
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

        # 5. Tenta enviar e-mail de confirmação (não crítico para o cadastro em si)
        try:
            # A função enviar_email_confirmacao agora gera o token JWT internamente
            sucesso_email = enviar_email_confirmacao(email, nome, user_id)
            if not sucesso_email:
                logger.warning(f"Falha ao enviar email de confirmação para {email}. Continue sem confirmação.")
        except Exception as e:
            logger.warning(f"Exceção ao enviar email de confirmação para {email}: {e}")

        logger.info(f"✅ Usuário {email} cadastrado com ID {user_id}")
        return True, "Conta criada com sucesso. Verifique seu e-mail para confirmar."

    except Exception as e:
        logger.exception("Erro inesperado ao cadastrar usuário")
        return False, f"Erro interno ao criar conta: {e}"

# =========================
# Verificação de Credenciais (Login)
# =========================
def verificar_credenciais(email: str, senha: str) -> Tuple[bool, Any]:
    """
    Verifica credenciais do usuário no Supabase.
    Retorna (True, user_data_dict) em caso de sucesso ou (False, mensagem de erro).
    """
    try:
        email = email.strip().lower()
        if not email or not senha:
            return False, "E-mail e senha são obrigatórios."

        ok, usuario_db = supabase_table_select(
            TABELA_USUARIOS,
            "id, nome, email, senha_hash, tipo, pais, email_confirmado, ativo, is_admin",
            {"email": email},
            single=True
        )

        if not ok:
            logger.error(f"Erro ao buscar usuário para {email}: {usuario_db}")
            return False, "Erro interno ao verificar credenciais."

        if not usuario_db:
            # Mensagem genérica para segurança
            return False, "E-mail ou senha incorretos."

        # Verifica se a conta está ativa
        if not usuario_db.get("ativo"):
            return False, "Sua conta está inativa. Entre em contato com o suporte."

        # Verifica se o e-mail foi confirmado (descomente se for obrigatório)
        # if not usuario_db.get("email_confirmado"):
        #     return False, "Por favor, confirme seu e-mail para fazer login."

        # Verifica a senha
        if not verify_password(senha, usuario_db["senha_hash"]):
            return False, "E-mail ou senha incorretos."

        logger.info(f"✅ Login bem-sucedido para {email}")
        # Retorna os dados do usuário (sem o hash da senha)
        user_data = {
            "id": usuario_db["id"],
            "nome": usuario_db["nome"],
            "email": usuario_db["email"],
            "tipo": usuario_db["tipo"],
            "pais": usuario_db["pais"],
            "email_confirmado": usuario_db["email_confirmado"],
            "ativo": usuario_db["ativo"],
            "is_admin": usuario_db["is_admin"],
        }
        return True, user_data

    except Exception as e:
        logger.exception("Erro inesperado ao verificar credenciais")
        return False, "Erro interno ao verificar credenciais."

# =========================
# Buscar Usuário
# =========================
def buscar_usuario_por_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Busca usuário por ID no Supabase."""
    try:
        ok, usuario_db = supabase_table_select(
            TABELA_USUARIOS,
            "id, nome, email, tipo, pais, email_confirmado, ativo, is_admin",
            {"id": user_id},
            single=True
        )
        if not ok or not usuario_db:
            return None
        # Garante que booleanos sejam booleanos
        usuario_db["email_confirmado"] = bool(usuario_db.get("email_confirmado"))
        usuario_db["ativo"] = bool(usuario_db.get("ativo"))
        usuario_db["is_admin"] = bool(usuario_db.get("is_admin"))
        return usuario_db
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por ID {user_id}: {e}", exc_info=True)
        return None

def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca usuário por e-mail no Supabase."""
    try:
        email = email.strip().lower()
        ok, usuario_db = supabase_table_select(
            TABELA_USUARIOS,
            "id, nome, email, tipo, pais, email_confirmado, ativo, is_admin",
            {"email": email},
            single=True
        )
        if not ok or not usuario_db:
            return None
        # Garante que booleanos sejam booleanos
        usuario_db["email_confirmado"] = bool(usuario_db.get("email_confirmado"))
        usuario_db["ativo"] = bool(usuario_db.get("ativo"))
        usuario_db["is_admin"] = bool(usuario_db.get("is_admin"))
        return usuario_db
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por e-mail {email}: {e}", exc_info=True)
        return None

# =========================
# Atualização de Usuário
# =========================
def atualizar_usuario(
    user_id: int,
    nome: Optional[str] = None,
    email: Optional[str] = None,
    tipo: Optional[str] = None, # Renomeado de tipo_usuario para tipo
    pais: Optional[str] = None,
    email_confirmado: Optional[bool] = None,
    ativo: Optional[bool] = None,
    is_admin: Optional[bool] = None,
) -> Tuple[bool, str]:
    """
    Atualiza dados do usuário no Supabase.
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        dados_update = {"atualizado_em": datetime.now().isoformat()}
        if nome:
            dados_update["nome"] = nome.strip()
        if email:
            if not validar_email(email):
                return False, "Novo e-mail inválido."
            # Verifica se o novo e-mail já existe para outro usuário
            ok, existing_user = supabase_table_select(
                TABELA_USUARIOS, "id", {"email": email.lower()}, single=True
            )
            if ok and existing_user and existing_user["id"] != user_id:
                return False, "O novo e-mail já está em uso por outro usuário."
            dados_update["email"] = email.strip().lower()
        if tipo:
            dados_update["tipo"] = tipo
        if pais:
            dados_update["pais"] = pais
        if email_confirmado is not None:
            dados_update["email_confirmado"] = email_confirmado
        if ativo is not None:
            dados_update["ativo"] = ativo
        if is_admin is not None:
            dados_update["is_admin"] = is_admin

        if not dados_update: # Se não há nada para atualizar além do timestamp
            return False, "Nenhum dado fornecido para atualização."

        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS,
            dados_update,
            {"id": user_id}
        )
        if ok_update:
            logger.info(f"✅ Usuário {user_id} atualizado com sucesso.")
            return True, "Usuário atualizado com sucesso."
        else:
            logger.error(f"Erro ao atualizar usuário {user_id}: {resultado_update}")
            return False, f"Erro ao atualizar usuário: {resultado_update}"
    except Exception as e:
        logger.exception(f"Erro inesperado ao atualizar usuário {user_id}")
        return False, f"Erro interno ao atualizar usuário: {e}"

def atualizar_tipo_usuario(user_id: int, novo_tipo: str) -> Tuple[bool, str]:
    """Atualiza o tipo de usuário (ex: Tutor, Veterinário, Admin)."""
    return atualizar_usuario(user_id, tipo=novo_tipo)

def atualizar_status_usuario(user_id: int, novo_status: bool) -> Tuple[bool, str]:
    """Ativa ou desativa a conta do usuário."""
    return atualizar_usuario(user_id, ativo=novo_status)

def alterar_senha(user_id: int, senha_atual: str, nova_senha: str, confirmar_nova_senha: str) -> Tuple[bool, str]:
    """
    Permite ao usuário alterar sua própria senha, exigindo a senha atual.
    """
    try:
        if not senha_atual or not nova_senha or not confirmar_nova_senha:
            return False, "Preencha todos os campos de senha."
        if nova_senha != confirmar_nova_senha:
            return False, "A nova senha e a confirmação não coincidem."
        if len(nova_senha) < 8:
            return False, "A nova senha deve ter pelo menos 8 caracteres."

        # 1. Busca a senha hash atual do usuário
        ok, usuario_db = supabase_table_select(
            TABELA_USUARIOS, "senha_hash", {"id": user_id}, single=True
        )
        if not ok or not usuario_db:
            return False, "Usuário não encontrado ou erro ao buscar senha."

        # 2. Verifica se a senha atual fornecida está correta
        if not verify_password(senha_atual, usuario_db["senha_hash"]):
            return False, "Senha atual incorreta."

        # 3. Gera hash da nova senha e atualiza
        nova_senha_hash = hash_password(nova_senha)
        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS,
            {"senha_hash": nova_senha_hash, "atualizado_em": datetime.now().isoformat()},
            {"id": user_id}
        )
        if ok_update:
            logger.info(f"✅ Senha do usuário {user_id} alterada com sucesso.")
            return True, "Senha alterada com sucesso."
        else:
            logger.error(f"Erro ao alterar senha do usuário {user_id}: {resultado_update}")
            return False, f"Erro ao alterar senha: {resultado_update}"
    except Exception as e:
        logger.exception(f"Erro inesperado ao alterar senha do usuário {user_id}")
        return False, f"Erro interno ao alterar senha: {e}"

# =========================
# Deleção de Usuário
# =========================
def deletar_usuario(user_id: int) -> Tuple[bool, str]:
    """
    Deleta um usuário do Supabase.
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        ok_delete, resultado_delete = supabase_table_delete(TABELA_USUARIOS, {"id": user_id})
        if ok_delete:
            logger.info(f"✅ Usuário {user_id} deletado com sucesso.")
            return True, "Usuário deletado com sucesso."
        else:
            logger.error(f"Erro ao deletar usuário {user_id}: {resultado_delete}")
            return False, f"Erro ao deletar usuário: {resultado_delete}"
    except Exception as e:
        logger.exception(f"Erro inesperado ao deletar usuário {user_id}")
        return False, f"Erro interno ao deletar usuário: {e}"

# Funções de compatibilidade (mantidas para evitar quebras em outros módulos)
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

