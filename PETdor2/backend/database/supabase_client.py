# PETdor2/backend/database/supabase_client.py

import os
import streamlit as st
from typing import Any, Dict, List, Optional, Tuple, Union

from supabase import create_client
from supabase.lib.client import APIResponse


# --------------------------------------------------------
# Criar cliente Supabase
# --------------------------------------------------------
def get_supabase():
    try:
        if "streamlit" in os.environ.get("STREAMLIT_VERSION", ""):
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
        else:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "SUPABASE_URL/SUPABASE_ANON_KEY ausentes. "
                "Verifique .env ou secrets.toml."
            )

        return create_client(supabase_url, supabase_key)

    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {e}")
        raise


# --------------------------------------------------------
# Testar conexão
# --------------------------------------------------------
def testar_conexao():
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()
        st.success("✅ Conexão com Supabase OK!")
        return True
    except Exception as e:
        st.error(f"❌ Falha ao testar conexão: {e}")
        return False


# --------------------------------------------------------
# SELECT Genérico
# --------------------------------------------------------
def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False
):
    try:
        client = get_supabase()

        query = client.from_(tabela).select(colunas)

        if filtros:
            for c, v in filtros.items():
                query = query.eq(c, v)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        resp: APIResponse = query.execute()

        if resp.data is None:
            return True, {} if single else []

        return True, resp.data

    except Exception as e:
        return False, f"Erro SELECT em {tabela}: {e}"


# --------------------------------------------------------
# INSERT
# --------------------------------------------------------
def supabase_table_insert(tabela: str, dados: Dict[str, Any]):
    try:
        client = get_supabase()
        resp: APIResponse = client.from_(tabela).insert(dados).execute()
        return True, resp.data
    except Exception as e:
        return False, f"Erro INSERT em {tabela}: {e}"


# --------------------------------------------------------
# UPDATE
# --------------------------------------------------------
def supabase_table_update(tabela: str, dados: Dict[str, Any], filtros: Dict[str, Any]):
    try:
        client = get_supabase()
        query = client.from_(tabela).update(dados)

        for c, v in filtros.items():
            query = query.eq(c, v)

        resp = query.execute()
        return True, resp.data
    except Exception as e:
        return False, f"Erro UPDATE em {tabela}: {e}"


# --------------------------------------------------------
# DELETE
# --------------------------------------------------------
def supabase_table_delete(tabela: str, filtros: Dict[str, Any]):
    try:
        client = get_supabase()
        query = client.from_(tabela).delete()

        for c, v in filtros.items():
            query = query.eq(c, v)

        resp = query.execute()
        qtd = len(resp.data) if resp.data else 0
        return True, qtd
    except Exception as e:
        return False, f"Erro DELETE em {tabela}: {e}"
