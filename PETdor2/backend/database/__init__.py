# backend/database/__init__.py
"""
Inicializa e expõe funções do cliente Supabase de forma simplificada.
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
    "
