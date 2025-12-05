# PETdor2/especies/__init__.py

"""
Pacote de espécies - configurações de avaliação de dor por tipo animal.
Gerencia o registro dinâmico de espécies e suas escalas de avaliação.
"""

from .base import EspecieConfig, Pergunta
from .index import (
    registrar_especie,
    buscar_especie_por_id,
    listar_especies,
    get_especies_nomes,
    get_especies_ids,
    get_escala_labels,
)

__all__ = [
    "EspecieConfig",
    "Pergunta",
    "registrar_especie",
    "buscar_especie_por_id",
    "listar_especies",
    "get_especies_nomes",
    "get_especies_ids",
    "get_escala_labels",
]
