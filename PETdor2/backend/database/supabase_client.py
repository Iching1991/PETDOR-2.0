# PETdor2/backend/database/supabase_client.py
"""
Cliente Supabase centralizado - usa variáveis de ambiente: SUPABASE_URL, SUPABASE_ANON_KEY
"""
import os
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from supabase import create_client, Client
from postgrest.base_request_builder import APIResponse # Importar para tipagem de response.data

logger = logging.getLogger(__name__)

# Singleton para o cliente Supabase
_supabase_client: Client | None = None

def get_supabase() -> Client:
    """Retorna instância singleton do cliente Supabase."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        logger.error("❌ SUPABASE_URL ou SUPABASE_ANON_KEY não configurados.")
        raise RuntimeError(
            "SUPABASE_URL ou SUPABASE_ANON_KEY não configurados. "
            "Verifique seu arquivo .env ou as variáveis de ambiente do Streamlit Cloud."
        )
    try:
        _supabase_client = create_client(url, key)
        logger.info("✅ Cliente Supabase inicializado com sucesso.")
        return _supabase_client
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}", exc_info=True)
        raise

def testar_conexao() -> bool:
    """
    Testa a conexão com o Supabase tentando buscar um registro de uma tabela de teste.
    Retorna True se a conexão for bem-sucedida, False caso contrário.
    """
    try:
        client = get_supabase()
        # Tenta buscar um registro de uma tabela que se espera que exista (ex: 'usuarios')
        # Limita a 1 para ser rápido e não carregar muitos dados.
        # Não precisa de filtros, apenas verificar se a query não falha.
        response = client.from_("usuarios").select("id").limit(1).execute()
        # Se a execução não levantar exceção e a resposta for válida, a conexão está ok.
        if response.data is not None: # Verifica se a resposta não é None, indicando sucesso
            logger.info("✅ Conexão com Supabase testada com sucesso.")
            return True
        else:
            logger.warning("⚠️ Conexão com Supabase testada, mas sem dados retornados (tabela 'usuarios' pode estar vazia ou inacessível).")
            return True # Consideramos sucesso se não houver erro, mesmo que vazia
    except Exception as e:
        logger.error(f"❌ Falha ao testar conexão com Supabase: {e}", exc_info=True)
        return False

def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None, # Adicionado para ordenação
    desc: bool = False, # Adicionado para ordenação
    single: bool = False
) -> Tuple[bool, Union[List[Dict[str, Any]], Dict[str, Any], str]]:
    """
    SELECT genérico no Supabase.
    Args:
        tabela: Nome da tabela.
        colunas: String de colunas a selecionar (ex: "id, nome, email").
        filtros: Dicionário com os filtros (ex: {"email": "teste@exemplo.com"}).
        order_by: Coluna para ordenar os resultados.
        desc: Se True, ordena em ordem decrescente.
        single: Se True, espera um único resultado.
    Returns:
        (True, dados) em caso de sucesso, (False, mensagem de erro) caso contrário.
        Dados pode ser uma lista de dicts, um único dict ou uma string de erro.
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).select(colunas)

        if filtros:
            for coluna, valor in filtros.items():
                query = query.eq(coluna, valor)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        response: APIResponse = query.execute() # Tipagem mais específica

        # Verifica se response.data é None (nenhum resultado) ou um dict/list vazio
        if response.data is None:
            return True, {} if single else [] # Retorna dict vazio para single, lista vazia para múltiplos

        return True, response.data
    except Exception as e:
        logger.error(f"Erro no SELECT em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao buscar dados: {e}"

def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    INSERT genérico no Supabase.
    Args:
        tabela: Nome da tabela.
        dados: Dicionário com os dados a inserir.
    Returns:
        (True, dados_inseridos) em caso de sucesso, (False, mensagem de erro) caso contrário.
        Dados inseridos é uma lista de dicts.
    """
    try:
        client = get_supabase()
        response: APIResponse = client.from_(tabela).insert(dados).execute()
        if response.data:
            logger.info(f"✅ Inserido em {tabela}: {response.data}")
            return True, response.data
        logger.warning(f"⚠️ Inserção em {tabela} não retornou dados, mas não houve erro.")
        return False, "Falha ao inserir dados ou nenhum dado retornado."
    except Exception as e:
        logger.error(f"Erro na inserção em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao inserir dados: {e}"

def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    UPDATE genérico no Supabase.
    Args:
        tabela: Nome da tabela.
        dados_update: Dicionário com os dados a atualizar.
        filtros: Dicionário com os filtros para identificar os registros.
    Returns:
        (True, dados_atualizados) em caso de sucesso, (False, mensagem de erro) caso contrário.
        Dados atualizados é uma lista de dicts.
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).update(dados_update)
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        response: APIResponse = query.execute()
        if response.data:
            logger.info(f"✅ Atualizado em {tabela}: {response.data}")
            return True, response.data
        logger.warning(f"⚠️ Atualização em {tabela} não afetou registros.")
        return False, "Nenhum registro foi atualizado."
    except Exception as e:
        logger.error(f"Erro na atualização em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao atualizar dados: {e}"

def supabase_table_delete(
    tabela: str,
    filtros: Dict[str, Any]
) -> Tuple[bool, int]:
    """
    DELETE genérico no Supabase.
    Args:
        tabela: Nome da tabela.
        filtros: Dicionário com os filtros para identificar os registros.
    Returns:
        (True, numero_de_registros_deletados) em caso de sucesso, (False, 0) caso contrário.
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).delete()
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        response: APIResponse = query.execute()
        # response.data pode ser uma lista vazia se nada foi deletado, mas a operação foi bem-sucedida
        num_deletados = len(response.data) if response.data else 0
        if num_deletados > 0:
            logger.info(f"✅ Deletado em {tabela}: {num_deletados} registro(s)")
            return True, num_deletados
        logger.warning(f"⚠️ Deleção em {tabela} não afetou registros.")
        return False, 0
    except Exception as e:
        logger.error(f"Erro na deleção em {tabela}: {e}", exc_info=True)
        return False, 0

