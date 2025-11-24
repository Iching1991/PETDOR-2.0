# PETdor2/database/supabase_client.py
"""
Módulo de cliente Supabase para acesso ao banco de dados.
Utiliza a biblioteca oficial supabase-py para operações com o banco.
"""
import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Se não estiverem definidas, tenta usar as credenciais do PostgreSQL
if not SUPABASE_URL or not SUPABASE_KEY:
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")

    if DB_HOST and DB_NAME and DB_USER:
        # Constrói a URL do Supabase a partir das credenciais PostgreSQL
        SUPABASE_URL = f"https://{DB_HOST.split('.')[0]}.supabase.co"
        SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
        logger.warning("⚠️ Usando credenciais PostgreSQL para construir URL Supabase")
    else:
        raise ValueError(
            "❌ Variáveis de ambiente não estão definidas corretamente.\n"
            "Configure SUPABASE_URL e SUPABASE_KEY ou DB_HOST, DB_NAME, DB_USER."
        )

# Cria o cliente Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Cliente Supabase inicializado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
    raise

def testar_conexao() -> bool:
    """
    Testa a conexão com o Supabase.

    Returns:
        bool: True se a conexão foi bem-sucedida, False caso contrário
    """
    try:
        response = supabase.table("usuarios").select("id").limit(1).execute()
        logger.info("✅ Conexão com Supabase testada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão com Supabase: {e}")
        return False

__all__ = ["supabase", "testar_conexao"]
