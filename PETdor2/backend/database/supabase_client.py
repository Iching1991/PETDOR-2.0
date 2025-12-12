# PETdor2/backend/database/supabase_client.py

import os
import streamlit as st
from typing import Any, Dict, List, Optional, Tuple, Union
from supabase import create_client, Client

# ----------------------------
# Inicialização global do cliente
# ----------------------------

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """
    Retorna uma instância única do cliente Supabase.
    Funciona tanto no Streamlit Cloud quanto local.
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    try:
        # STREAMLIT CLOUD — usa secrets
        if "streamlit" in os.environ.get("STREAMLIT_VERSION", ""):
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]

        else:
            # LOCAL — usa .env
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "❌ SUPABASE_URL ou SUPABASE_ANON_KEY ausentes. "
                "Configure no Streamlit Secrets ou .env"
            )

        _supabase_client = create_client(supabase_url, supabase_key)
        return _supabase_client

    except Exception as e:
        st.error(f"❌ Erro ao inicializar Supabase: {e}")
        raise


# ----------------------------
# Testar conexão
# ----------------------------

def testar_conexao() -> bool:
    """Verifica se a conexão com Supabase está funcionando."""
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(0).execute()
        st.success("✅ Conexão com Supabase funcionando!")
        return True
    except Exception as e:
        st.error(f"❌ Falha ao testar conexão: {e}")
        return False


# ----------------------------
# Funções de banco
# ----------------------------

def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False
) -> Tuple[bool, Union[List[Dict[str, Any]], Dict[str, Any], str]]:
    """SELECT genérico."""
    try:
        client = get_supabase()
        query = client.table(tabela).select(colunas)

        if filtros:
            for col, val in filtros.items():
                query = query.eq(col, val)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        response = query.execute()

        return True, response.data if response.data else ({} if single else [])

    except Exception as e:
        return False, f"Erro ao buscar dados: {e}"


def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """INSERT genérico."""
    try:
        client = get_supabase()
        response = client.table(tabela).insert(dados).execute()

        return True, response.data if response.data else []
    except Exception as e:
        return False, f"Erro ao inserir dados: {e}"


def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """UPDATE genérico."""
    try:
        client = get_supabase()
        query = client.table(tabela).update(dados_update)

        for col, val in filtros.items():
            query = query.eq(col, val)

        response = query.execute()
        return True, response.data if response.data else []

    except Exception as e:
        return False, f"Erro ao atualizar: {e}"


def supabase_table_delete(
    tabela: str,
    filtros: Dict[str, Any]
) -> Tuple[bool, int]:
    """DELETE genérico."""
    try:
        client = get_supabase()
        query = client.table(tabela).delete()

        for col, val in filtros.items():
            query = query.eq(col, val)

        response = query.execute()
        return True, len(response.data or [])

    except Exception as e:
        return False, 0
