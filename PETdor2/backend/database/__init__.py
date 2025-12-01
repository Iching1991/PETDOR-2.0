# PetDor2/database/__init__.py
"""
Módulo de inicialização do pacote database.
Exporta funções para interação com o Supabase.
"""

# Importa e reexporta as funções do cliente Supabase
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
