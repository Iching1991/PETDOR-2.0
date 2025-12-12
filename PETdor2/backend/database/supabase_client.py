# backend/database/supabase_client.py

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Tuple

load_dotenv()

# =====================================================
# Carregar credenciais
# =====================================================
def carregar_credenciais():
    # Prioridade: secrets.toml
    if "supabase" in st.secrets:
        url = st.secrets["supabase"].get("SUPABASE_URL")
        key = st.secrets["supabase"].get("SUPABASE_KEY")

        if url and key:
            return url, key

    # Fallback: .env
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    return url, key


# =====================================================
# Criar cliente Supabase
# =====================================================
def get_supabase() -> Client:
    url, key = carregar_credenciais()

    if not url or not key:
        raise RuntimeError("Variáveis do Supabase não configuradas.")

    try:
        client = create_client(url, key)  # ✔️ sem proxy, sem parâmetros extras
        return client
    except Exception as e:
        raise RuntimeError(f"Erro ao criar cliente Supabase: {e}")


# =====================================================
# Testar conexão
# =====================================================
def testar_conexao() -> bool:
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()
        return True
    except Exception as e:
        st.error(f"❌ Falha ao conectar ao Supabase: {e}")
        return False


# =====================================================
# SELECT
# =====================================================
def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False
) -> Tuple[bool, Any]:
    try:
        client = get_supabase()
        query = client.table(tabela).select(colunas)

        if filtros:
            for k, v in filtros.items():
                query = query.eq(k, v)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        resp = query.execute()
        return True, resp.data or {}

    except Exception as e:
        return False, f"Erro no SELECT: {e}"


# =====================================================
# INSERT
# =====================================================
def supabase_table_insert(tabela: str, dados: Dict[str, Any]):
    try:
        client = get_supabase()
        resp = client.table(tabela).insert(dados).execute()
        return True, resp.data
    except Exception as e:
        return False, f"Erro no INSERT: {e}"


# =====================================================
# UPDATE
# =====================================================
def supabase_table_update(tabela: str, dados_update: Dict[str, Any], filtros: Dict[str, Any]):
    try:
        client = get_supabase()
        query = client.table(tabela).update(dados_update)

        for k, v in filtros.items():
            query = query.eq(k, v)

        resp = query.execute()
        return True, resp.data

    except Exception as e:
        return False, f"Erro no UPDATE: {e}"


# =====================================================
# DELETE
# =====================================================
def supabase_table_delete(tabela: str, filtros: Dict[str, Any]):
    try:
        client = get_supabase()
        query = client.table(tabela).delete()

        for k, v in filtros.items():
            query = query.eq(k, v)

        resp = query.execute()
        deleted = len(resp.data) if resp.data else 0
        return True, deleted

    except Exception as e:
        return False, f"Erro no DELETE: {e}"
