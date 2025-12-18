import streamlit as st
import requests
from typing import Optional, Dict, Any, List

def get_supabase_client():
    """
    Retorna as credenciais do Supabase configuradas via Streamlit Secrets.
    """
    try:
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]
        return {"url": url, "key": key}
    except Exception as e:
        st.error(f"Erro ao carregar credenciais do Supabase: {e}")
        return None

def get_headers_with_jwt() -> Dict[str, str]:
    """
    Retorna headers HTTP com JWT do usuário logado (se existir).

    Returns:
        Dicionário com headers incluindo Authorization
    """
    client = get_supabase_client()
    if not client:
        return {}

    headers = {
        "apikey": client["key"],
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    # Se houver token JWT na sessão, adiciona ao header
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    else:
        # Usa a chave anon como fallback
        headers["Authorization"] = f"Bearer {client['key']}"

    return headers

def supabase_table_select(
    table: str,
    select: str = "*",
    filters: Optional[Dict[str, Any]] = None,
    order: Optional[str] = None,
    limit: Optional[int] = None
) -> Optional[List[Dict]]:
    """
    Executa SELECT em uma tabela do Supabase via REST API.
    """
    client = get_supabase_client()
    if not client:
        return None

    url = f"{client['url']}/rest/v1/{table}"
    headers = get_headers_with_jwt()

    params = {"select": select}

    if filters:
        for key, value in filters.items():
            if isinstance(value, bool):
                params[key] = f"eq.{str(value).lower()}"
            else:
                params[key] = f"eq.{value}"

    if order:
        params["order"] = order

    if limit:
        params["limit"] = limit

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao consultar tabela {table}: {e}")
        return None

def supabase_table_insert(
    table: str,
    data: Dict[str, Any]
) -> Optional[Dict]:
    """
    Insere um registro em uma tabela do Supabase via REST API.
    """
    client = get_supabase_client()
    if not client:
        return None

    url = f"{client['url']}/rest/v1/{table}"
    headers = get_headers_with_jwt()

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result[0] if result else None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao inserir em {table}: {e}")
        return None

def supabase_table_update(
    table: str,
    filters: Dict[str, Any],
    data: Dict[str, Any]
) -> Optional[List[Dict]]:
    """
    Atualiza registros em uma tabela do Supabase via REST API.
    """
    client = get_supabase_client()
    if not client:
        return None

    url = f"{client['url']}/rest/v1/{table}"
    headers = get_headers_with_jwt()

    params = {}
    if filters:
        for key, value in filters.items():
            params[key] = f"eq.{value}"

    try:
        response = requests.patch(url, headers=headers, params=params, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao atualizar {table}: {e}")
        return None

def supabase_table_delete(
    table: str,
    filters: Dict[str, Any]
) -> bool:
    """
    Deleta registros de uma tabela do Supabase via REST API.
    """
    client = get_supabase_client()
    if not client:
        return False

    url = f"{client['url']}/rest/v1/{table}"
    headers = get_headers_with_jwt()

    params = {}
    if filters:
        for key, value in filters.items():
            params[key] = f"eq.{value}"

    try:
        response = requests.delete(url, headers=headers, params=params)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao deletar de {table}: {e}")
        return False

def testar_conexao() -> bool:
    """
    Testa a conexão com o Supabase.
    """
    result = supabase_table_select("usuarios", limit=1)
    return result is not None
