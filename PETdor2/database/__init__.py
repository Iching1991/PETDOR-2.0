# PETdor2/database/__init__.py
"""
Pacote para gerenciamento de banco de dados do PETDOR.
Contém módulos para conexão, migração e modelos de dados.
"""
import logging
import os
# Não importa sqlite3 aqui, pois estamos focando em PostgreSQL
# from sqlite3 import Row # Não é necessário para PostgreSQL

# Importações relativas para módulos dentro do pacote database
from . import connection
from . import migration
# from . import models # Se você tiver um módulo models.py

logger = logging.getLogger(__name__)

# Exponha as funções/objetos que devem ser acessíveis diretamente do pacote database
__all__ = ["connection", "migration"] # Adicione "models" se tiver
