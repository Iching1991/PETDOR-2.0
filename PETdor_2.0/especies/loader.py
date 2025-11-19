# PETdor_2.0/especies/loader.py

"""
Módulo para carregar e gerenciar dados de espécies.
"""

from .index import get_especies_nomes # Importa de especies.index agora!

def listar_especies():
    """
    Retorna uma lista de nomes de espécies disponíveis para seleção.
    """
    return get_especies_nomes()

# Exemplo de uso (opcional, para testes)
if __name__ == "__main__":
    print("Espécies listadas pelo loader:", listar_especies())
