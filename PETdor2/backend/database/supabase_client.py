# backend/database/supabase_client.py

import os
import streamlit as st
from supabase import create_client

# =====================================================
# 1) OBTER CREDENCIAIS DO SUPABASE
# =====================================================

def load_credentials():
    """
    Carrega as credenciais do Supabase a partir do Streamlit secrets
    ou de variáveis de ambiente locais.
    """
    try:
        if "supabase" in st.secrets:
            url = st.secrets["supabase"].get("SUPABASE_URL")
            key = st.secrets["supabase"].get("SUPABASE_KEY") or \
                  st.secrets["supabase"].get("SUPABASE_ANON_KEY")
        else:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            raise ValueError("Variáveis do Supabase não configuradas.")

        return url, key

    except Exception as e:
        st.error(f"❌ Erro ao carregar credenciais do Supabase: {e}")
        return None, None


# =====================================================
# 2) CRIAR CLIENTE SUPABASE
# =====================================================

def get_supabase():
    """
    Cria e retorna o cliente Supabase.
    Compatível com supabase-py v2.x (NÃO aceita proxy).
    """
    url, key = load_credentials()

    if not url or not key:
        st.error("❌ Variáveis do Supabase não configuradas.")
        raise RuntimeError("Credenciais ausentes.")

    try:
        client = create_client(url, key)
        return client

    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {e}")
        raise


# =====================================================
# 3) TESTAR CONEXÃO
# =====================================================

def testar_conexao() -> bool:
    """ Testa a conexão consultando a tabela 'usuarios'. """
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()
        return True

    except Exception as e:
        st.error(f"❌ Falha ao conectar ao Supabase: {e}")
        return False


# =====================================================
# 4) SELECT
# =====================================================

def supabase_table_select(tabela: str, colunas="*", filtros=None, order_by=None, desc=False, single=False):
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
        return True, resp.data

    except Exception as e:
        return False, f"Erro no SELECT: {e}"


# =====================================================
# 5) INSERT
# =====================================================

def supabase_table_insert(tabela: str, dados: dict):
    try:
        client = get_supabase()
        resp = client.table(tabela).insert(dados).execute()
        return True, resp.data

    except Exception as e:
        return False, f"Erro no INSERT: {e}"


# =====================================================
# 6) UPDATE
# =====================================================

def supabase_table_update(tabela: str, dados_update: dict, filtros: dict):
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
# 7) DELETE
# =====================================================

def supabase_table_delete(tabela: str, filtros: dict):
    try:
        client = get_supabase()
        query = client.table(tabela).delete()

        for k, v in filtros.items():
            query = query.eq(k, v)

        resp = query.execute()
        return True, len(resp.data) if resp.data else 0

    except Exception as e:
        return False, f"Erro no DELETE: {e}"
