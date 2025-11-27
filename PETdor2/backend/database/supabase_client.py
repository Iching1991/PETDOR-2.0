# PETdor2/backend/database/supabase_client.py
"""
Cliente oficial do Supabase usando Python SDK
Compatível com Streamlit Cloud e sem conexão direta com PostgreSQL.
"""

import os
import streamlit as st
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

def get_secret(key: str, default: str = None):
    """Lê secret do Streamlit Cloud ou variável de ambiente."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

supabase: Client = None

def get_supabase() -> Client:
    """Inicializa cliente Supabase (singleton)."""
    global supabase

    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("❌ SUPABASE_URL ou SUPABASE_KEY não configurados")

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado")

    return supabase


# ---------- CRUD GENÉRICO ---------- #

def inserir(tabela: str, dados: dict):
    try:
        db = get_supabase()
        resp = db.table(tabela).insert(dados).execute()
        if resp.error:
            return False, str(resp.error)
        return True, resp.data
    except Exception as e:
        return False, str(e)


def buscar(tabela: str, coluna=None, valor=None):
    try:
        db = get_supabase()
        query = db.table(tabela).select("*")

        if coluna:
            query = query.eq(coluna, valor)

        resp = query.execute()

        if resp.error:
            return False, str(resp.error)
        
        return True, resp.data
    except Exception as e:
        return False, str(e)


def buscar_um(tabela: str, coluna, valor):
    ok, dados = buscar(tabela, coluna, valor)
    if not ok:
        return False, dados
    return True, dados[0] if dados else None


def atualizar(tabela: str, coluna, valor, novos_dados: dict):
    try:
        db = get_supabase()
        resp = (
            db.table(tabela)
            .update(novos_dados)
            .eq(coluna, valor)
            .execute()
        )
        if resp.error:
            return False, str(resp.error)
        return True, resp.data
    except Exception as e:
        return False, str(e)


def deletar(tabela: str, coluna, valor):
    try:
        db = get_supabase()
        resp = (
            db.table(tabela)
            .delete()
            .eq(coluna, valor)
            .execute()
        )
        if resp.error:
            return False, str(resp.error)
        return True, resp.data
    except Exception as e:
        return False, str(e)


__all__ = [
    "get_supabase",
    "inserir",
    "buscar",
    "buscar_um",
    "atualizar",
    "deletar",
]

