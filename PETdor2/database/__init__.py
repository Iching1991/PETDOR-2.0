"""
Pacote de acesso ao banco de dados da aplicação PETDor.

Este módulo inicializa o pacote 'database', tornando seus submódulos
(connection, migration, models) acessíveis.

Para evitar ciclos de importação, funções específicas como 'criar_tabelas'
não são importadas diretamente para o namespace do pacote aqui.
Em vez disso, importe-as diretamente do módulo 'database.migration'
onde forem necessárias (ex: no streamlit_app.py).
"""

# Importa os submódulos para que possam ser acessados via database.connection, database.migration, etc.
from . import connection
from . import migration
from . import models

# Exponha apenas o que é estritamente necessário ou que não cause ciclos.
# Neste caso, estamos expondo os módulos em si, para que você possa usar
# database.connection.conectar_db, database.migration.criar_tabelas, etc.
__all__ = [
    "connection",
    "migration",
    "models",
]

# Se você realmente precisar de conectar_db diretamente como database.conectar_db,
# pode adicioná-lo aqui, pois 'connection' não depende de 'migration' ou 'models'.
from .connection import conectar_db
__all__.append("conectar_db")
