# PETdor2/backend/auth/user.py

from typing import Optional, Dict, Any
from backend.database import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete
)


# --------------------------------------------------------
# Criar usuário
# --------------------------------------------------------
def criar_usuario(dados: Dict[str, Any]):
    return supabase_table_insert("usuarios", dados)


# --------------------------------------------------------
# Buscar por email
# --------------------------------------------------------
def buscar_usuario_por_email(email: str):
    return supabase_table_select(
        tabela="usuarios",
        filtros={"email": email},
        single=True
    )


# --------------------------------------------------------
# Autenticar
# --------------------------------------------------------
def autenticar_usuario(email: str, senha_hash: str):
    ok, usuario = buscar_usuario_por_email(email)

    if not ok or not usuario:
        return False, "Usuário não encontrado."

    if usuario.get("senha") != senha_hash:
        return False, "Senha incorreta."

    return True, usuario


# --------------------------------------------------------
# Atualizar dados
# --------------------------------------------------------
def atualizar_usuario(user_id: str, dados: Dict[str, Any]):
    return supabase_table_update(
        "usuarios",
        dados_update=dados,
        filtros={"id": user_id}
    )


# --------------------------------------------------------
# Deletar usuário
# --------------------------------------------------------
def deletar_usuario(user_id: str):
    return supabase_table_delete("usuarios", {"id": user_id})
