# PETdor2/backend/database/supabase_client.py

import os
import streamlit as st
from supabase import create_client
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
#   CRIAÇÃO DO CLIENTE SUPABASE
# ============================================================
def get_supabase():
    """
    Retorna o client do Supabase utilizando st.secrets (produção)
    ou variáveis de ambiente locais (.env).
    """
    try:
        if "streamlit" in os.environ.get("STREAMLIT_VERSION", ""):
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
        else:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("Variáveis SUPABASE_URL e SUPABASE_ANON_KEY não configuradas.")

        return create_client(supabase_url, supabase_key)

    except Exception as e:
        st.error(f"❌ Erro ao criar cliente Supabase: {e}")
        raise


# ============================================================
#   TESTE DE CONEXÃO
# ============================================================
def testar_conexao() -> bool:
    """
    Realiza um SELECT simples para validar a conexão.
    """
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()

        st.success("✅ Conexão com o Supabase estabelecida!")
        return True

    except Exception as e:
        st.error(f"❌ Falha ao testar conexão com Supabase: {e}")
        return False


# ============================================================
#   SELECT GENÉRICO
# ============================================================
def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False
) -> Tuple[bool, Any]:
    """
    SELECT genérico no Supabase.
    """
    try:
        client = get_supabase()
        query = client.table(tabela).select(colunas)

        if filtros:
            for coluna, valor in filtros.items():
                query = query.eq(coluna, valor)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        response = query.execute()

        return True, response.data or []

    except Exception as e:
        return False, f"Erro ao buscar dados: {e}"


# ============================================================
#   INSERT GENÉRICO
# ============================================================
def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, Any]:
    try:
        client = get_supabase()
        response = client.table(tabela).insert(dados).execute()

        return True, response.data

    except Exception as e:
        return False, f"Erro ao inserir dados: {e}"


# ============================================================
#   UPDATE GENÉRICO
# ============================================================
def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, Any]:
    try:
        client = get_supabase()
        query = client.table(tabela).update(dados_update)

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response = query.execute()
        return True, response.data or []

    except Exception as e:
        return False, f"Erro ao atualizar dados: {e}"


# ============================================================
#   DELETE GENÉRICO
# ============================================================
def supabase_table_delete(
    tabela: str,
    filtros: Dict[str, Any]
) -> Tuple[bool, int]:
    try:
        client = get_supabase()
        query = client.table(tabela).delete()

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response = query.execute()

        deleted_count = len(response.data or [])

        return True, deleted_count

    except Exception as e:
        return False, 0
