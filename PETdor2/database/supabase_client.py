# PETdor2/database/supabase_client.py
"""
Módulo de cliente Supabase para acesso ao banco de dados.
"""
import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validação das credenciais
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error(
        "❌ Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não estão definidas.\n"
        "Configure-as no Streamlit Cloud: Settings → Secrets"
    )
    raise ValueError(
        "❌ Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não estão definidas.\n"
        "Configure-as no Streamlit Cloud: Settings → Secrets"
    )

# Cria o cliente Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Cliente Supabase inicializado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}")
    raise

def testar_conexao() -> bool:
    """Testa a conexão com o Supabase."""
    try:
        response = supabase.table("usuarios").select("id").limit(1).execute()
        logger.info("✅ Conexão com Supabase testada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão: {e}")
        return False

__all__ = ["supabase", "testar_conexao"]
