# PETdor2/backend/database/supabase_client.py
# PETdor2/backend/database/supabase_client.py
"""
Cliente Supabase centralizado - usa Streamlit Secrets em vez de variáveis de ambiente.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st  # <- Para acessar st.secrets
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Singleton do cliente Supabase
_supabase_client: Client | None = None

def get_supabase() -> Client:
    """Retorna instância singleton do cliente Supabase usando st.secrets."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    try:
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]

        _supabase_client = create_client(url, key)
        logger.info("✅ Cliente Supabase inicializado com sucesso (via Streamlit Secrets).")
        return _supabase_client
    except KeyError as e:
        raise RuntimeError(f"Chave {e} não encontrada em st.secrets") from e
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}", exc_info=True)
        raise

def testar_conexao() -> bool:
    """Testa a conexão com o Supabase."""
    try:
        client = get_supabase()
        response = client.from_("usuarios").select("id").limit(1).execute()
        if response.data is not None:
            logger.info("✅ Conexão Supabase testada com sucesso.")
            return True
        else:
            logger.warning("⚠️ Conexão Supabase estabelecida, mas select simples não retornou dados.")
            return True
    except Exception as e:
        logger.error(f"❌ Falha ao testar conexão Supabase: {e}", exc_info=True)
        return False

# Funções genéricas (SELECT, INSERT, UPDATE, DELETE) podem ser mantidas iguais
def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    single: bool = False
) -> Tuple[bool, List[Dict[str, Any]] | Dict[str, Any] | str]:
    try:
        client = get_supabase()
        query = client.from_(tabela).select(colunas)
        if filtros:
            for coluna, valor in filtros.items():
                query = query.eq(coluna, valor)
        if single:
            query = query.single()
        response = query.execute()
        return True, response.data if response.data is not None else ([] if not single else {})
    except Exception as e:
        logger.error(f"Erro no SELECT em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao buscar dados: {e}"

def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    try:
        client = get_supabase()
        response = client.from_(tabela).insert(dados).execute()
        if response.data:
            return True, response.data
        return False, "Falha ao inserir dados."
    except Exception as e:
        logger.error(f"Erro na inserção em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao inserir dados: {e}"

def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    try:
        client = get_supabase()
        query = client.from_(tabela).update(dados_update)
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        response = query.execute()
        if response.data:
            return True, response.data
        return False, "Nenhum registro foi atualizado."
    except Exception as e:
        logger.error(f"Erro na atualização em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao atualizar dados: {e}"

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
        return (True, len(response.data)) if response.data else (False, 0)
    except Exception as e:
        logger.error(f"Erro na deleção em {tabela}: {e}", exc_info=True)
        return False, 0
