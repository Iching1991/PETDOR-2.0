# PETdor_2.0/especies/__init__.py

"""
Módulo de inicialização do pacote 'especies'.
Expõe funções para listar e obter configurações de espécies.
"""

# Importa o módulo index, que agora contém as classes Pergunta e EspecieConfig
# e as funções de registro e busca de espécies.
from . import index
from . import loader # Importa o módulo loader para que ele seja parte do pacote

# Exponha as funções e classes que você deseja que sejam acessíveis diretamente
# do pacote 'especies'.
__all__ = [
    "index",
    "loader",
    "Pergunta", # Expondo Pergunta e EspecieConfig diretamente do pacote
    "EspecieConfig",
    "get_especies_nomes",
    "get_especie_config",
]

# Importa as funções e classes específicas para o namespace do pacote
# para que possam ser acessadas como especies.get_especies_nomes()
from .index import Pergunta, EspecieConfig, get_especies_nomes, get_especie_config
