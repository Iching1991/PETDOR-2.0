# PETdor_2.0/especies/porquinho.py

"""
🐹 Configuração de avaliação para PORQUINHOS-DA-ÍNDIA
Escala: 0 a 7 — baseada em sinais comportamentais e clínicos.
"""
from especies.index import EspecieConfig, Pergunta

CONFIG_PORQUINHO = EspecieConfig(
    nome="Porquinho-da-Índia",
    especie_id="porquinho", # <-- CORREÇÃO: Adicionado o campo especie_id aqui!
    descricao="Avaliação de dor em porquinhos-da-índia — Escala de 0 (nunca) a 7 (sempre).",
    opcoes_escala=[
        "0 - Nunca", "1 - Raramente", "2 - Às vezes", "3 - Frequentemente",
        "4 - Quase Sempre", "5 - Sempre", "6 - Muito Frequente", "7 - Constante"
    ],
    perguntas=[
        # Postura e Movimentação
        Pergunta(texto="Meu porquinho-da-índia está curvado ou imóvel por longos períodos", invertida=False, peso=1.0),
        Pergunta(texto="Meu porquinho-da-índia reduziu suas atividades diárias", invertida=False, peso=1.0),
        Pergunta(texto="Meu porquinho-da-índia evita correr ou explorar", invertida=False, peso=1.0),
        # Alimentação
        Pergunta(texto="O apetite diminuiu ou está comendo mais devagar", invertida=False, peso=1.0),
        Pergunta(texto="O consumo de água diminuiu", invertida=False, peso=1.0),
        # Vocalização e Comportamento
        Pergunta(texto="Ele vocaliza diferente (gritos, chiados ou sons incomuns)", invertida=False, peso=1.0),
        Pergunta(texto="Ele reage com dor ao toque ou manipulação", invertida=False, peso=1.0),
        Pergunta(texto="Ele se esconde mais do que o habitual", invertida=False, peso=1.0),
        # Aparência Geral
        Pergunta(texto="Ele está menos limpo ou com pelos arrepiados", invertida=False, peso=1.0),
        Pergunta(texto="A respiração parece mais rápida ou difícil", invertida=False, peso=1.0),
    ]
)


