# PETdor2/backend/database/__init__.py
"""
Módulo de banco de dados - Supabase PostgreSQL
"""
from .supabase_client import (
    get_connection,
    testar_conexao,
    executar_query,
    buscar_dados,
    buscar_um,
    inserir_dados,
    atualizar_dados,
    deletar_dados,
)

__all__ = [
    "get_connection",
    "testar_conexao",
    "executar_query",
    "buscar_dados",
    "buscar_um",
    "inserir_dados",
    "atualizar_dados",
    "deletar_dados",
]
