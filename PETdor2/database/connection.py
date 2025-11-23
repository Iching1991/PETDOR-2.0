# PETdor2/database/connection.py

import os
import sqlite3
import psycopg2
import psycopg2.extras
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Caminho do SQLite local (fallback)
BASE_DIR = Path(__file__).resolve().parent.parent
SQLITE_DB_PATH = BASE_DIR / "petdor.db"

# Detecta se deve usar PostgreSQL (SUPABASE)
USANDO_POSTGRES = bool(os.getenv("DB_HOST"))


# ==========================================================
# Conectar ao PostgreSQL (Supabase)
# ==========================================================
def conectar_postgres():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        logger.info("Conectado ao PostgreSQL (Supabase).")
        return conn

    except Exception as e:
        logger.error(f"Erro ao conectar no PostgreSQL: {e}", exc_info=True)
        raise ConnectionError("Não foi possível conectar ao banco PostgreSQL.")


# ==========================================================
# Conectar ao SQLite (fallback local)
# ==========================================================
def conectar_sqlite():
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        logger.warning("Usando SQLite (modo local).")
        return conn

    except Exception as e:
        logger.error(f"Erro ao conectar SQLite: {e}", exc_info=True)
        raise ConnectionError("Falha ao abrir o banco SQLite.")


# ==========================================================
# Conexão principal (automática)
# ==========================================================
def conectar_db():
    """
    Decide automaticamente qual banco conectar:
    - Se existir DB_HOST → PostgreSQL (Supabase)
    - Caso contrário → SQLite local
    """
    if USANDO_POSTGRES:
        return conectar_postgres()
    return conectar_sqlite()

