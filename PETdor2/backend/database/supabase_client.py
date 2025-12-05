# PETdor2/backend/database/supabase_client.py
"""
"""
Cliente Supabase via REST API – compatível com Python 3.13
Substitui completamente o antigo create_client.
"""

import os
import logging
import requests
from typing import Any, Dict, Optional, Tuple, List

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("As variáveis SUPABASE_URL e SUPABASE_ANON_KEY não estão configuradas.")

# URL da REST API
REST_URL = f"{SUPABASE_URL}/rest/v1"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def testar_conexao() -> Tuple[bool, str]:
    """Testa a conexão fazendo um SELECT simples."""
    try:
        url = f"{REST_URL}/usuarios?select=id&limit=1"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code in (200, 204):
            return True, "Conexão com Supabase OK!"
        else:
            return False, f"Erro HTTP {response.status_code}: {response.text}"

    except Exception as e:
        return False, f"Falha: {e}"


def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    single: bool = False
) -> Tuple[bool, Any]:

    try:
        params = {"select": colunas}

        if filtros:
            for chave, valor in filtros.items():
                params[chave] = f"eq.{valor}"

        url = f"{REST_URL}/{tabela}"
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            return False, f"Erro: {response.text}"

        data = response.json()
        if single:
            return True, (data[0] if data else None)
        return True, data

    except Exception as e:
        return False, f"Erro SELECT: {e}"


def supabase_table_insert(tabela: str, dados: Dict[str, Any]) -> Tuple[bool, Any]:
    try:
        url = f"{REST_URL}/{tabela}"
        response = requests.post(url, headers=HEADERS, json=dados)

        if response.status_code not in (200, 201):
            return False, response.text

        return True, response.json()

    except Exception as e:
        return False, f"Erro INSERT: {e}"


def supabase_table_update(tabela: str, dados_update: Dict[str, Any], filtros: Dict[str, Any]) -> Tuple[bool, Any]:
    try:
        params = {}
        for chave, valor in filtros.items():
            params[chave] = f"eq.{valor}"

        url = f"{REST_URL}/{tabela}"
        response = requests.patch(url, headers=HEADERS, json=dados_update, params=params)

        if response.status_code != 200:
            return False, response.text

        return True, response.json()

    except Exception as e:
        return False, f"Erro UPDATE: {e}"


def supabase_table_delete(tabela: str, filtros: Dict[str, Any]) -> Tuple[bool, int]:
    try:
        params = {}
        for chave, valor in filtros.items():
            params[chave] = f"eq.{valor}"

        url = f"{REST_URL}/{tabela}"
        response = requests.delete(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            return False, 0

        return True, len(response.json())

    except Exception as e:
        return False, 0
