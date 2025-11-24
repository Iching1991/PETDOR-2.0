# PETdor2/database/__init__.py
"""
Pacote de banco de dados - gerencia conexões com Supabase.
"""
from .supabase_client import get_supabase, testar_conexao

__all__ = ["get_supabase", "testar_conexao"]

