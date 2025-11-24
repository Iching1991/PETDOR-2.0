# PETdor2/database/__init__.py
"""
Pacote para gerenciamento de banco de dados do PETDOR.
Gerencia conexões e operações com Supabase.
"""
import logging

logger = logging.getLogger(__name__)

# Importa apenas o cliente Supabase
from database.supabase_client import supabase

# Exponha o cliente Supabase para uso em todo o projeto
__all__ = ["supabase"]
