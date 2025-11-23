# PETdor2/database/supabase_client.py
import os
import requests
import logging

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def supabase_table_select(table_name: str, limit: int = 10):
    """Retorna dados de uma tabela"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit={limit}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        logger.error(f"Erro ao consultar tabela {table_name}: {e}", exc_info=True)
        return None, str(e)

def supabase_table_insert(table_name: str, data: dict):
    """Insere um registro em uma tabela"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table_name}"
        response = requests.post(url, json=data, headers=HEADERS)
        response.raise_for_status()
        return True, None
    except Exception as e:
        logger.error(f"Erro ao inserir na tabela {table_name}: {e}", exc_info=True)
        return False, str(e)

def testar_conexao() -> bool:
    """Testa a conexão com a tabela 'usuarios'"""
    data, err = supabase_table_select("usuarios", limit=1)
    if err:
        print(f"Erro ao testar Supabase: {err}")
        return False
    return True
