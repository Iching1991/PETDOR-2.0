"""
Pacote de acesso ao banco de dados da aplicação PETDor.

Responsável por:
- Conexão com o banco SQLite (módulo connection)
- Criação e migração das tabelas (módulo migration)
- Funções de acesso a dados (módulo models)
"""

# Importa os módulos para que possam ser acessados via database.connection, database.migration, etc.
from . import connection
from . import migration
from . import models

# Expõe as funções e módulos que você deseja que sejam facilmente acessíveis
# diretamente do pacote 'database'.
# Note que estamos expondo as funções 'criar_tabelas' e 'migrar_banco_completo'
# diretamente do módulo 'migration' para o namespace do pacote 'database'.
# Isso é o que você tinha originalmente e o que vamos tentar fazer funcionar.
from .connection import conectar_db
from .migration import criar_tabelas, migrar_banco_completo

__all__ = [
    "connection",
    "migration",
    "models",
    "conectar_db",
    "criar_tabelas",
    "migrar_banco_completo",
]
