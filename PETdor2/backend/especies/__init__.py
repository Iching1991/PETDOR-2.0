# PETdor2/especies/__init__.py
"""
Pacote de espécies do PETDor2.
Registra e disponibiliza todas as espécies do sistema.
"""

from .index import (
    EspecieConfig,
    Pergunta,
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
