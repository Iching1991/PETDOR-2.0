# PETdor_2.0/especies/__init__.py

"""
Pacote para gerenciamento de configurações de espécies.
Define as estruturas de dados para perguntas e configurações de espécies,
e gerencia o registro e acesso a essas configurações.
"""

from .index import ( # <-- Importa diretamente de index
    EspecieConfig,
    Pergunta,
    listar_especies,
    buscar_especie_por_id,
    get_especies_nomes # <-- Adicionado para ser compatível com avaliacao.py
)

# Opcional: definir __all__ para controle de importação
__all__ = [
    "EspecieConfig",
    "Pergunta",
    "listar_especies",
    "buscar_especie_por_id",
    "get_especies_nomes"
]

# Importa as funções e classes específicas para o namespace do pacote
# para que possam ser acessadas como especies.get_especies_nomes()
from .index import Pergunta, EspecieConfig, get_especies_nomes, get_especie_config

