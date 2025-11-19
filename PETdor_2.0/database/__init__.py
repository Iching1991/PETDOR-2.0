"""
Módulo de inicialização do pacote database.
Expõe funções essenciais para conexão e migração do banco de dados.
"""
from .connection import conectar_db
# Não importamos criar_tabelas e migrar_banco_completo diretamente aqui
# para evitar possíveis ciclos de importação com o streamlit_app.py
# que também importa migration.
# Se precisar acessá-los via database.<funcao>, importe o módulo migration
# e use database.migration.<funcao> ou importe diretamente no arquivo que precisa.

__all__ = ["conectar_db"] # Apenas conectar_db será exposto diretamente pelo pacote database
