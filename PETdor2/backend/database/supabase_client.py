# PetDor2/database/supabase_client.py
"""
Cliente Supabase centralizado - substitui SQLite connection.py
Usa variáveis de ambiente: SUPABASE_URL, SUPABASE_ANON_KEY
"""

import os
import logging
from typing import Any, Dict, List, Optional, Tuple
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Singleton para o cliente Supabase
_supabase_client: Client | None = None

def get_supabase() -> Client:
    """Retorna instância singleton do cliente Supabase (equivalente a conectar_db())."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL ou SUPABASE_ANON_KEY não configurados. "
            "Verifique seu arquivo .env ou as variáveis de ambiente do Streamlit Cloud."
        )

    try:
        _supabase_client = create_client(url, key)
        logger.info("✅ Cliente Supabase inicializado com sucesso (substituindo SQLite).")
        return _supabase_client
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}", exc_info=True)
        raise

def testar_conexao() -> bool:
    """Testa a conexão fazendo uma query simples (equivalente ao teste de conexão SQLite)."""
    try:
        client = get_supabase()
        response = client.table("usuarios").select("count(*)").limit(1).execute()
        logger.info("✅ Teste de conexão com Supabase bem-sucedido.")
        return True
    except Exception as e:
        logger.error(f"❌ Falha no teste de conexão com Supabase: {e}", exc_info=True)
        return False

# =========================
# Funções Helper Genéricas (substituem queries SQL diretas)
# =========================

def supabase_table_select(
    tabela: str, 
    colunas: str = "*", 
    filtros: Dict[str, Any] = None, 
    single: bool = False
) -> Tuple[bool, Any]:
    """
    SELECT genérico no Supabase (substitui SELECT SQL).

    Args:
        tabela: Nome da tabela (ex: "usuarios")
        colunas: Colunas a selecionar (ex: "*", "id, nome, email")
        filtros: Dict com filtros (ex: {"email": "user@example.com"})
        single: True para .single(), False para lista

    Returns:
        (sucesso, dados) — onde dados é o resultado da query ou mensagem de erro
    """
    try:
        client = get_supabase()
        query = client.table(tabela).select(colunas)

        # Aplica filtros se fornecidos (substitui WHERE)
        if filtros:
            for coluna, valor in filtros.items():
                query = query.eq(coluna, valor)

        if single:
            response = query.single().execute()
            dados = response.data if response.data else None
        else:
            response = query.execute()
            dados = response.data if response.data else []

        return True, dados

    except Exception as e:
        logger.error(f"Erro na query SELECT em {tabela}: {e}", exc_info=True)
        return False, f"Erro na consulta: {str(e)}"

def supabase_table_insert(
    tabela: str, 
    dados: Dict[str, Any]
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    INSERT genérico no Supabase (substitui INSERT SQL).

    Args:
        tabela: Nome da tabela
        dados: Dict com os dados a inserir

    Returns:
        (sucesso, lista_de_registros_inseridos)
    """
    try:
        client = get_supabase()
        response = client.table(tabela).insert(dados).execute()
        if response.data:
            logger.info(f"✅ Inserido em {tabela}: {len(response.data)} registro(s)")
            return True, response.data
        else:
            logger.warning(f"⚠️  Inserção em {tabela} não retornou dados")
            return False, []

    except Exception as e:
        logger.error(f"Erro na inserção em {tabela}: {e}", exc_info=True)
        return False, [f"Erro na inserção: {str(e)}"]

def supabase_table_update(
    tabela: str, 
    dados: Dict[str, Any], 
    filtros: Dict[str, Any]
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    UPDATE genérico no Supabase (substitui UPDATE SQL).

    Args:
        tabela: Nome da tabela
        dados: Dict com os dados a atualizar
        filtros: Dict com os filtros (ex: {"id": 1})

    Returns:
        (sucesso, lista_de_registros_atualizados)
    """
    try:
        client = get_supabase()
        query = client.table(tabela).update(dados)

        # Aplica filtros (substitui WHERE)
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response = query.execute()
        if response.data:
            logger.info(f"✅ Atualizado em {tabela}: {len(response.data)} registro(s)")
            return True, response.data
        else:
            logger.warning(f"⚠️  Atualização em {tabela} não afetou registros")
            return False, []

    except Exception as e:
        logger.error(f"Erro na atualização em {tabela}: {e}", exc_info=True)
        return False, ["Erro na atualização: {str(e)}"]

def supabase_table_delete(
    tabela: str, 
    filtros: Dict[str, Any]
) -> Tuple[bool, int]:
    """
    DELETE genérico no Supabase (substitui DELETE SQL).

    Args:
        tabela: Nome da tabela
        filtros: Dict com os filtros (ex: {"id": 1})

    Returns:
        (sucesso, numero_de_registros_deletados)
    """
    try:
        client = get_supabase()
        query = client.table(tabela).delete()

        # Aplica filtros (substitui WHERE)
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response = query.execute()
        if response.data:
            logger.info(f"✅ Deletado em {tabela}: {len(response.data)} registro(s)")
            return True, len(response.data)
        else:
            logger.warning(f"⚠️  Deleção em {tabela} não afetou registros")
            return False, 0

    except Exception as e:
        logger.error(f"Erro na deleção em {tabela}: {e}", exc_info=True)
        return False, 0
