# PETdor2/database/supabase_client.py
"""
Módulo de cliente Supabase para acesso ao banco de dados.
Usa lazy loading para evitar erros de inicialização.
"""
import os
import logging
from typing import Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Variáveis globais
_supabase_client: Optional[Client] = None

def get_supabase() -> Client:
    """
    Retorna o cliente Supabase, criando-o se necessário (lazy loading).

    Returns:
        Client: Cliente Supabase inicializado

    Raises:
        ValueError: Se as credenciais não estiverem configuradas
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    # Carrega as variáveis de ambiente
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Validação
    if not SUPABASE_URL or not SUPABASE_KEY:
        error_msg = (
            "❌ Variáveis de ambiente não configuradas:\n"
            "- SUPABASE_URL\n"
            "- SUPABASE_KEY\n\n"
            "Configure-as no Streamlit Cloud: Settings → Secrets"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Cliente Supabase inicializado com sucesso")
        return _supabase_client
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Supabase: {e}")
        raise

# Alias para compatibilidade com código existente
@property
def supabase() -> Client:
    """Propriedade para acessar o cliente Supabase."""
    return get_supabase()

def testar_conexao() -> bool:
    """Testa a conexão com o Supabase."""
    try:
        client = get_supabase()
        response = client.table("usuarios").select("id").limit(1).execute()
        logger.info("✅ Conexão com Supabase testada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão: {e}")
        return False

__all__ = ["get_supabase", "testar_conexao"]
