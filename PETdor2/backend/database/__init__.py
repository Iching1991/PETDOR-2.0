# PetDor2/backend/database/__init__.py
"""
Pacote de acesso a dados do PETDor2 (Supabase v2)
Expondo funções principais para uso geral.
"""

from .supabase_client import (
    get_supabase,
    testar_conexao,
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

__all__ = [
    "get_supabase",
    "testar_conexao",
    "supabase_table_select",
    "supabase_table_insert",
    "supabase_table_update",
    "supabase_table_delete",
]
