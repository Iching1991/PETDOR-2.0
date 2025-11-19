# PETdor_2.0/especies/coelho.py

"""
🐇 Configuração de avaliação para COELHOS
Escala: 0 a 7 — baseada no Rabbit Grimace Scale e parâmetros comportamentais.
"""
from especies.index import EspecieConfig, Pergunta

CONFIG_COELHO = EspecieConfig(
    nome="Coelho",
    especie_id="coelho", # <-- CORREÇÃO: Adicionado o campo especie_id aqui!
    descricao="Avaliação de dor em coelhos — Escala de 0 (nunca) a 7 (sempre).",
    opcoes_escala=[
        "0 - Nunca", "1 - Raramente", "2 - Às vezes", "3 - Frequentemente",
        "4 - Quase Sempre", "5 - Sempre", "6 - Muito Frequente", "7 - Constante"
    ],
    perguntas=[
        # Postura e Movimentação
        Pergunta(texto="Meu coelho está com postura anormal (curvado, imóvel)", invertida=False, peso=1.0),
        Pergunta(texto="Meu coelho está menos ativo ou se movimenta pouco", invertida=False, peso=1.0),
        Pergunta(texto="Meu coelho evita saltar ou explorar o ambiente", invertida=False, peso=1.0),

        # Expressão Facial
        Pergunta(texto="Meu coelho apresenta olhos semicerrados ou expressão tensa", invertida=False, peso=1.0),
        Pergunta(texto="As bochechas ou nariz parecem tensos ou retraídos", invertida=False, peso=1.0),

        # Alimentação e Higiene
        Pergunta(texto="O apetite do meu coelho reduziu", invertida=False, peso=1.0),
        Pergunta(texto="Meu coelho reduziu a ingestão de água", invertida=False, peso=1.0),
        Pergunta(texto="Meu coelho está menos limpo ou parou de se lamber", invertida=False, peso=1.0),

        # Comportamento e Interação
        Pergunta(texto="Meu coelho se esconde mais do que o normal", invertida=False, peso=1.0),
        Pergunta(texto="Meu coelho reage com dor quando tocado", invertida=False, peso=1.0),
    ]
)


