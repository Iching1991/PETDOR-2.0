# PETdor2/database/__init__.py
"""
Pacote para gerenciamento de banco de dados do PETDOR.
Contém módulos para migração e modelos de dados usando Supabase.
"""
import logging
# Inicializa o pacote database
from . import migration
from . import models
from . import supabase_client


logger = logging.getLogger(__name__)

# Exponha os módulos que devem ser acessíveis diretamente do pacote database
__all__ = ["migration", "models", "supabase_client"]

