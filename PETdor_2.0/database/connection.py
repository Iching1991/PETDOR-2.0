# PETdor_2.0/database/connection.py
"""
Conexão inteligente: PostgreSQL (Supabase) na nuvem ou SQLite local.
"""
import os
import sqlite3
import logging

# Para PostgreSQL (Supabase)
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logging.warning("psycopg2 não instalado. PostgreSQL indisponível.")

logger = logging.getLogger(__name__)

# ------------- SQLite (desenvolvimento local) -------------
def conectar_db_sqlite():
    """Conecta ao SQLite local (petdor.db)."""
    db_dir = "data"
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "petdor.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    logger.info(f"Conectado ao SQLite: {db_path}")
    return conn

# ------------- PostgreSQL (Supabase - produção) -------------
def conectar_db_supabase():
    """Conecta ao PostgreSQL no Supabase."""
    if not POSTGRES_AVAILABLE:
        raise RuntimeError("psycopg2 não instalado. Instale com: pip install psycopg2-binary")

    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT", "5432")

    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        raise RuntimeError("Variáveis de ambiente do Supabase não configuradas (DB_HOST, DB_NAME, etc.)")

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode="require",  # Supabase exige SSL
            cursor_factory=psycopg2.extras.DictCursor,
        )
        logger.info("Conectado ao Supabase (PostgreSQL)")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar no Supabase: {e}")
        raise

# ------------- Função principal: escolhe o banco certo -------------
def conectar_db():
    """
    Conecta ao banco apropriado automaticamente:
    - Supabase (PostgreSQL) se DB_HOST estiver configurado (produção)
    - SQLite local se não (desenvolvimento)
    """
    if os.getenv("DB_HOST") and POSTGRES_AVAILABLE:
        logger.info("Usando Supabase (PostgreSQL) - produção")
        return conectar_db_supabase()
    else:
        logger.info("Usando SQLite local - desenvolvimento")
        return conectar_db_sqlite()

# ------------- Função de teste de conexão -------------
def testar_conexao_supabase():
    """Testa se consegue conectar no Supabase e listar tabelas."""
    try:
        if not POSTGRES_AVAILABLE:
            return False, "psycopg2 não instalado"

        if not os.getenv("DB_HOST"):
            return False, "DB_HOST não configurado nos Secrets"

        conn = conectar_db_supabase()
        cur = conn.cursor()
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        tabelas = [row[0] for row in cur.fetchall()]
        conn.close()

        logger.info(f"Conexão Supabase OK. Tabelas: {tabelas}")
        return True, f"Conexão OK. Tabelas encontradas: {tabelas}"

    except Exception as e:
        logger.error(f"Falha na conexão Supabase: {e}")
        return False, str(e)

