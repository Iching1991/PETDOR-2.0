# PETdor2/database/supabase_client.py
"""
Cliente Supabase para o PETDOR.
Configura a conexão com o backend Supabase usando variáveis de ambiente.
"""

import os
from supabase import create_client, Client

# Pega as variáveis de ambiente (recomendado não deixar hardcoded)
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://seuprojeto.supabase.co")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "sua_chave_anon_publica")

# Cria o cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Opcional: função utilitária para teste da conexão
def testar_conexao() -> bool:
    """
    Retorna True se conseguir se conectar e listar tabelas.
    """
    try:
        response = supabase.table("usuarios").select("*").limit(1).execute()
        if response.error:
            print(f"Erro ao testar Supabase: {response.error}")
            return False
        return True
    except Exception as e:
        print(f"Exceção ao testar Supabase: {e}")
        return False
