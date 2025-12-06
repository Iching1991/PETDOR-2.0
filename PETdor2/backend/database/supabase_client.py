# PETdor2/backend/database/supabase_client.py
import os
import logging
from supabase import create_client, SupabaseClient
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def get_supabase() -> SupabaseClient:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL ou SUPABASE_KEY não estão definidos no ambiente.")

    return create_client(url, key)


def testar_conexao() -> Tuple[bool, Optional[str]]:
    """Testa se a conexão com o Supabase está funcionando."""
    try:
        supabase = get_supabase()
        response = supabase.from_("test_table").select("*").limit(1).execute()
        return True, None
    except Exception as e:
        logger.error(f"Erro ao testar conexão Supabase: {e}")
        return False, str(e)


def supabase_table_select(table: str, query: dict = None) -> Any:
    """Consulta genérica em uma tabela."""
    try:
        supabase = get_supabase()
        q = supabase.from_(table).select("*")

        if query:
            for field, value in query.items():
                q = q.eq(field, value)

        response = q.execute()
        return response.data
    except Exception as e:
        logger.error(f"Erro ao consultar tabela {table}: {e}")
        return None
