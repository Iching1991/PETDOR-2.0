# PETdor2/especies/index.py
"""
Sistema central de registro e consulta das espécies e suas configurações.
Cada espécie deve fornecer um dicionário com a estrutura:
{
    "id": "cao",
    "nome": "Cães",
    "categorias": [
        {
            "nome": "Comportamento",
            "perguntas": [
                { "texto": "Está ativo?", "escala": "0-3" }
            ]
        }
    ]
}
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Onde todas as espécies são armazenadas
_ESPECIES_REGISTRADAS: Dict[str, dict] = {}

# ==========================================================
# Funções de registro e busca
# ==========================================================

def registrar_especie(config: dict):
    """
    Registra a configuração de uma espécie.
    A configuração DEVE conter:
        - id (str)
        - nome (str)
        - categorias (list)
    """
    especie_id = config.get("id")
    if not especie_id:
        raise ValueError("Configuração de espécie inválida: falta o campo 'id'.")
    if especie_id in _ESPECIES_REGISTRADAS:
        logger.warning(f"⚠️ Espécie com ID '{especie_id}' já registrada. Atualizando...")
    _ESPECIES_REGISTRADAS[especie_id] = config
    logger.info(f"✅ Espécie '{config.get('nome')}' registrada com sucesso")

def buscar_especie_por_id(especie_id: str) -> Optional[dict]:
    """Retorna a configuração completa da espécie."""
    return _ESPECIES_REGISTRADAS.get(especie_id)

def listar_especies() -> List[dict]:
    """Lista todas as espécies registradas."""
    return list(_ESPECIES_REGISTRADAS.values())

def get_especies_nomes() -> List[str]:
    """Retorna somente os nomes das espécies registradas."""
    return [config["nome"] for config in _ESPECIES_REGISTRADAS.values()]

def get_especies_ids() -> List[str]:
    """Retorna somente os IDs das espécies registradas."""
    return list(_ESPECIES_REGISTRADAS.keys())

def get_escala_labels(escala: str) -> List[str]:
    """
    Retorna os labels de uma escala.
    Exemplo:
        "0-3" → ["0", "1", "2", "3"]
        "sim-nao" → ["Sim", "Não"]
    """
    escala = escala.lower().strip()
    if escala == "sim-nao":
        return ["Sim", "Não"]
    if "-" in escala:
        try:
            inicio, fim = escala.split("-")
            return [str(i) for i in range(int(inicio), int(fim) + 1)]
        except ValueError:
            logger.error(f"Escala inválida: {escala}")
            raise ValueError(f"Escala desconhecida: {escala}")
    raise ValueError(f"Escala desconhecida: {escala}")

# ==========================================================
# Importar e registrar automaticamente todas as espécies
# ==========================================================

try:
    from .cao import CONFIG_CAES
    registrar_especie(CONFIG_CAES)
except Exception as e:
    logger.error(f"❌ Erro ao registrar cães: {e}")

try:
    from .gato import CONFIG_GATOS
    registrar_especie(CONFIG_GATOS)
except Exception as e:
    logger.error(f"❌ Erro ao registrar gatos: {e}")

try:
    from .coelho import CONFIG_COELHO
    registrar_especie(CONFIG_COELHO)
except Exception as e:
    logger.error(f"❌ Erro ao registrar coelhos: {e}")

try:
    from .porquinho import CONFIG_PORQUINHO
    registrar_especie(CONFIG_PORQUINHO)
except Exception as e:
    logger.error(f"❌ Erro ao registrar porquinhos: {e}")

try:
    from .aves import CONFIG_AVES
    registrar_especie(CONFIG_AVES)
except Exception as e:
    logger.error(f"❌ Erro ao registrar aves: {e}")

try:
    from .repteis import CONFIG_REPTEIS
    registrar_especie(CONFIG_REPTEIS)
except Exception as e:
    logger.error(f"❌ Erro ao registrar répteis: {e}")

logger.info(f"✅ Total de espécies registradas: {len(_ESPECIES_REGISTRADAS)}")

__all__ = [
    "registrar_especie",
    "buscar_especie_por_id",
    "listar_especies",
    "get_especies_nomes",
    "get_especies_ids",
    "get_escala_labels",
]
