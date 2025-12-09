  # PETdor2/backend/especies/base.py
  from dataclasses import dataclass, field
  from typing import List, Dict, Any

  @dataclass
  class Pergunta:
      id: str
      texto: str
      escala: str  # Ex: "0-7", "sim-nao"
      peso: float = 1.0  # Peso da pergunta na pontuação final

  @dataclass
  class EspecieConfig:
      id: str
      nome: str
      perguntas: List[Pergunta]
      limites_dor: Dict[str, str] = field(default_factory=dict)  # Ex: {"0-2": "Baixa", "3-5": "Média", "6-7": "Alta"}

      def to_dict(self):
          return {
              "id": self.id,
              "nome": self.nome,
              "perguntas": [p.__dict__ for p in self.perguntas],
              "limites_dor": self.limites_dor
          }
