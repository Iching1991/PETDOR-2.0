# PETdor_2.0/especies/index.py

"""
Módulo de registro e carregamento de configurações de espécies.
Define as dataclasses Pergunta e EspecieConfig e registra automaticamente
as configurações de cada espécie.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional # <-- CORREÇÃO: Adicionado 'Optional' aqui!

@dataclass
class Pergunta:
    texto: str
    invertida: bool = False
    peso: float = 1.0

@dataclass
class EspecieConfig:
    nome: str
    especie_id: str
    descricao: str
    opcoes_escala: List[str]
    perguntas: List[Pergunta]

# Dicionário para armazenar as configurações de todas as espécies
_ESPECIES_REGISTRADAS: Dict[str, EspecieConfig] = {}

def registrar_especie(config: EspecieConfig):
    """Registra uma configuração de espécie no sistema."""
    if config.especie_id in _ESPECIES_REGISTRADAS:
        raise ValueError(f"Espécie com ID '{config.especie_id}' já registrada.")
    _ESPECIES_REGISTRADAS[config.especie_id] = config

def listar_especies() -> List[EspecieConfig]:
    """Retorna uma lista de todas as configurações de espécies registradas."""
    return list(_ESPECIES_REGISTRADAS.values())

def buscar_especie_por_id(especie_id: str) -> Optional[EspecieConfig]:
    """Busca uma configuração de espécie pelo seu ID."""
    return _ESPECIES_REGISTRADAS.get(especie_id)

# ----------------------------------------------------------------------
# Importa e registra as configurações de cada espécie
# ----------------------------------------------------------------------
# Importa as configurações de cada arquivo de espécie
from .cao import CONFIG_CAES
from .gato import CONFIG_GATOS
from .coelho import CONFIG_COELHO
from .porquinho import CONFIG_PORQUINHO
from .aves import CONFIG_AVES
from .repteis import CONFIG_REPTEIS

# Registra as configurações importadas
registrar_especie(CONFIG_CAES)
registrar_especie(CONFIG_GATOS)
registrar_especie(CONFIG_COELHO)
registrar_especie(CONFIG_PORQUINHO)
registrar_especie(CONFIG_AVES)
registrar_especie(CONFIG_REPTEIS)
