# PETdor_2.0/especies/cao.py

"""
🐕 Configuração de avaliação para CÃES.
Escala: 0 a 7 (baseada em CBPI e Glasgow Composite Pain Scale).
"""
from .base import EspecieConfig, Pergunta

CONFIG_CAES = EspecieConfig(
    nome="Cachorro",
    especie_id="cao", # Adicionei o especie_id para consistência
    descricao="Avaliação de dor em cães - Escala de 0 (nunca) a 7 (sempre).",
    opcoes_escala=[
        "0 - Nunca",
        "1 - Raramente",
        "2 - Às vezes",
        "3 - Frequentemente",
        "4 - Quase Sempre",
        "5 - Sempre",
        "6 - Muito Frequente",
        "7 - Constante",
    ],
    perguntas=[
        # Energia e Atividade
        Pergunta(texto="Meu cão pouca energia", invertida=False, peso=1.0),
        Pergunta(texto="Meu cão foi brincalhão", invertida=True, peso=1.0),
        Pergunta(texto="Meu cão fez as suas atividades favoritas", invertida=True, peso=1.0),
        # Alimentação
        Pergunta(texto="O apetite do meu cão reduziu", invertida=False, peso=1.0),
        Pergunta(texto="Meu cão comeu normalmente a sua comida favorita", invertida=True, peso=1.0),
        # Mobilidade
        Pergunta(texto="Meu cão reluta para levantar", invertida=False, peso=1.0),
        Pergunta(texto="Meu cão teve problemas para levantar-se ou deitar-se", invertida=False, peso=1.0),
        Pergunta(texto="Meu cão teve problemas para caminhar", invertida=False, peso=1.0),
        Pergunta(texto="Meu cão caiu ou perdeu o equilíbrio", invertida=False, peso=1.0),
        # Comportamento Social
        Pergunta(texto="Meu cão gosta de estar perto de mim", invertida=True, peso=1.0),
        Pergunta(texto="Meu cão mostrou uma quantidade normal de afeto", invertida=True, peso=1.0),
        Pergunta(texto="Meu cão gostou de ser tocado ou acariciado", invertida=True, peso=1.0),
        # Comportamento Geral
        Pergunta(texto="Meu cão agiu normalmente", invertida=True, peso=1.0),
        Pergunta(texto="Meu cão teve problemas para ficar confortável", invertida=False, peso=1.0),
        # Sono
        Pergunta(texto="Meu cão dormiu bem durante a", invertida=True, peso=1.0),
    ],
)
