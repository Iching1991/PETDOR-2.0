# PETdor2/database/supabase_client.py
import os
from supabase import create_client, Client

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def testar_conexao() -> bool:
    try:
        response = supabase.table("usuarios").select("*").limit(1).execute()
        return response.error is None
    except Exception as e:
        print(f"Erro ao testar Supabase: {e}")
        return False
