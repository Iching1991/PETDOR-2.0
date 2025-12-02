# PetDor2/backend/database/__init__.py
"""
Camada de acesso a dados usando Supabase.
Exponha aqui apenas o que for realmente usado pelo resto do app.
"""

# Importa todas as funções do supabase_client.py e as expõe diretamente
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
