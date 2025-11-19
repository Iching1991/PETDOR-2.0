# PETdor_2.0/especies/aves.py

"""
🦜 Configuração de avaliação para AVES
Escala: 0 a 7 — com base em observação comportamental geral.
"""

from .index import EspecieConfig, Pergunta

CONFIG_AVES = EspecieConfig(
    nome="Aves",
    especie_id="aves",  # campo adicionado para identificação interna
    descricao="Avaliação de dor em aves — Escala de 0 (nunca) a 7 (sempre).",
    opcoes_escala=[
        "0 - Nunca", "1 - Raramente", "2 - Às vezes", "3 - Frequentemente",
        "4 - Quase Sempre", "5 - Sempre", "6 - Muito Frequente", "7 - Constante"
    ],
    perguntas=[
        # Postura e Mobilidade
        Pergunta(texto="Minha ave está com postura anormal (arrepiada, encolhida)", invertida=False, peso=1.0),
        Pergunta(texto="Minha ave reduziu a movimentação ou não voa mais", invertida=False, peso=1.0),

        # Alimentação e Hábito
        Pergunta(texto="Minha ave está comendo menos", invertida=False, peso=1.0),
        Pergunta(texto="Minha ave bebe menos água", invertida=False, peso=1.0),

        # Comportamento
        Pergunta(texto="Minha ave vocaliza menos ou de forma diferente", invertida=False, peso=1.0),
        Pergunta(texto="Minha ave evita contato ou fica mais agressiva", invertida=False, peso=1.0),

        # Aparência
        Pergunta(texto="Minha ave está com penas eriçadas ou desalinhadas", invertida=False, peso=1.0),
        Pergunta(texto="Minha ave fica muito tempo parada no mesmo lugar", invertida=False, peso=1.0),
    ],
)

