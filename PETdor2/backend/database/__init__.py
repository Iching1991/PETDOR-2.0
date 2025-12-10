# PETdor2/backend/database/__init__.py
"""
Pacote de gerenciamento de banco de dados para o PETdor2.
"""
# Não importe supabase_client aqui para evitar importação circular
# As funções de supabase_client serão importadas diretamente onde forem necessárias.

# Se você tiver outras funções que não dependem de supabase_client
# e que você queira expor no pacote database, importe-as aqui.
# Exemplo:
# from .migration import criar_tabelas, migrar_banco_completo

# Por enquanto, vamos deixar o __init__.py mais simples para resolver a circularidade.

__all__ = [
    # Se você tiver funções de migração ou outras que não causam circularidade,
    # adicione-as aqui.
    # "criar_tabelas",
    # "migrar_banco_completo",
]
