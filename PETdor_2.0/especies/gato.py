# PETdor_2.0/especies/gato.py

"""
🐈 Configuração de avaliação de dor para GATOS.
Escala: 0 a 7 (baseada em escalas de dor felina).
"""
from .base import EspecieConfig, Pergunta

CONFIG_GATOS = EspecieConfig(
    nome="Gato",
    especie_id="gato",
    descricao="Avaliação de dor em gatos - Escala de 0 (ausente) a 7 (severa).",
    opcoes_escala=[
        "0 - Ausente",
        "1 - Muito Leve",
        "2 - Leve",
        "3 - Moderada",
        "4 - Moderada a Severa",
        "5 - Severa",
        "6 - Muito Severa",
        "7 - Extrema",
    ],
    perguntas=[
        # Comportamento Geral
        Pergunta(texto="O gato está mais quieto ou menos ativo?", invertida=False, peso=1.0),
        Pergunta(texto="Há mudanças no apetite ou consumo de água?", invertida=False, peso=1.0),
        Pergunta(texto="O gato está se escondendo ou evitando interação?", invertida=False, peso=1.0),
        # Mobilidade
        Pergunta(texto="Há dificuldade para pular, subir ou se mover?", invertida=False, peso=1.0),
        Pergunta(texto="O gato está lambendo ou mordendo excessivamente alguma parte do corpo?", invertida=False, peso=1.0),
        # Postura e Expressão Facial
        Pergunta(texto="Há alterações na postura (ex: encurvado, cabeça baixa)?", invertida=False, peso=1.0),
        Pergunta(texto="O gato está com os olhos semicerrados ou com a face tensa?", invertida=False, peso=1.0),
        # Vocalização
        Pergunta(texto="O gato está vocalizando mais (miados, rosnados) ou menos do que o habitual?", invertida=False, peso=1.0),
        # Higiene
        Pergunta(texto="Há mudanças nos hábitos de higiene (ex: pelo desgrenhado)?", invertida=False, peso=1.0),
        # Sono
        Pergunta(texto="O gato está dormindo mais ou em posições incomuns?", invertida=False, peso=1.0),
    ],
)
