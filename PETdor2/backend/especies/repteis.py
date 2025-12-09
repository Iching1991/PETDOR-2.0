# PETdor2/backend/especies/repteis.py

"""
🦎 Configuração de avaliação para RÉPTEIS
⚠ Em construção — avaliação especializada ainda não disponível.
"""

# --------------------------------------------------------------
# 🚨 IMPORTAÇÃO CORRIGIDA (Antes estava from especies.index ❌)
# --------------------------------------------------------------
from .base import EspecieConfig, Pergunta


CONFIG_REPTEIS = EspecieConfig(
    nome="Répteis",
    especie_id="repteis", # <-- Adicionado o campo especie_id aqui!
    descricao="Avaliação de dor em répteis — Em construção.",
    opcoes_escala=["0 - Em desenvolvimento"],
    perguntas=[
        Pergunta(texto="Avaliação para esta espécie ainda está em desenvolvimento.", invertida=False, peso=0.0)
    ]
) # <-- PARÊNTESE FINAL ADICIONADO AQUI!
