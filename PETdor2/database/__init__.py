# PETdor2/database/__init__.py
import logging
import os
# Removido sqlite3 e Row, pois a conexão será com PostgreSQL (Supabase)
# from sqlite3 import Row 

# CORREÇÃO: Importação relativa para connection
from . import connection 
from .connection import conectar_db # Expondo conectar_db
from .migration import migrar_banco_completo # Expondo migrar_banco_completo

logger = logging.getLogger(__name__)

__all__ = ["conectar_db", "migrar_banco_completo"] # Atualizado para expor as funções corretas

# Docstring conforme memória
"""
Este pacote gerencia a conexão e migração do banco de dados para o PETDOR.
Ele abstrai os detalhes de conexão e garante que a estrutura do banco esteja atualizada.
"""
