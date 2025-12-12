# backend/database/supabase_client.py

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ===========================================================
# LEITURA DAS VARIÁVEIS
# ===========================================================
def load_supabase_env():
    """Carrega as credenciais do Supabase de secrets.toml ou .env"""
    if "supabase" in st.secrets:
        url = st.secrets["supabase"].get("SUPABASE_URL")
        key = st.secrets["supabase"].get("SUPABASE_KEY")
    else:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        raise RuntimeError("Variáveis do Supabase não configuradas.")

    return url, key


# ===========================================================
# CLIENTE DO SUPABASE
# ===========================================================
@st.cache_resource
def get_supabase() -> Client:
    """Cria um cliente global do Supabase (sem proxy, sem argumentos extras)"""

    try:
        supabase_url, supabase_key = load_supabase_env()
        supabase = create_client(supabase_url, supabase_key)
        return supabase

    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {e}")
        raise


# ===========================================================
# TESTE DE CONEXÃO
# ===========================================================
def testar_conexao() -> bool:
    """Executa um SELECT simples para testar se a conexão funciona"""
    try:
        client = get_supabase()
        resp = client.table("usuarios").select("*").limit(1).execute()
        return True
    except Exception as e:
        st.error(f"❌ Falha ao conectar ao Supabase: {e}")
        return False


# ===========================================================
# SELECT
# ===========================================================
def supabase_table_select(tabela: str, colunas: str = "*", filtros=None):
    try:
        client = get_supabase()
        query = client.table(tabela).select(colunas)

        if filtros:
            for k, v in filtros.items():
                query = query.eq(k, v)

        resp = query.execute()

        return True, resp.data

    except Exception as e:
        return False, f"Erro no SELECT: {e}"


# ===========================================================
# INSERT
# ===========================================================
def supabase_table_insert(tabela: str, dados: dict):
    try:
        client = get_supabase()
        resp = client.table(tabela).insert(dados).execute()
        return True, resp.data
    except Exception as e:
        return False, f"Erro no INSERT: {e}"


# ===========================================================
# UPDATE
# ===========================================================
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


# ===========================================================
# DELETE
# ===========================================================
def supabase_table_delete(tabela: str, filtros: dict):
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
