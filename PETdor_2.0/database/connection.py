# PETdor_2_0/database/connection.py
"""
Conexão inteligente: PostgreSQL (Supabase com pg8000) na nuvem ou SQLite local.
"""
import os
import sqlite3
import logging
from collections import namedtuple

logger = logging.getLogger(__name__)

# --- Cursor para retornar resultados como dicionários (compatível com SQLite) ---
# Para SQLite, sqlite3.Row já faz isso, mas mantemos a consistência
class DictCursor:
    """Cursor que retorna linhas como dicionários."""
    def __init__(self, cursor):
        self._cursor = cursor

    @property
    def description(self):
        return [d[0] for d in self._cursor.description]

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return dict(zip(self.description, row))

    def fetchall(self):
        rows = self._cursor.fetchall()
        if not rows:
            return []
        return [dict(zip(self.description, row)) for row in rows]

    def __getattr__(self, name):
        return getattr(self._cursor, name)

# ------------- SQLite (desenvolvimento local e fallback para produção) -------------
def conectar_db_sqlite():
    """Conecta ao SQLite local (petdor.db)."""
    db_dir = "data"
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "petdor.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row # sqlite3.Row já retorna como dicionário/namedtuple
    logger.info(f"Conectado ao SQLite: {db_path}")
    return conn

# ------------- Função principal: escolhe o banco certo (agora só SQLite) -------------
def conectar_db():
    """
    Conecta ao banco de dados SQLite local.
    Temporariamente desativando a conexão Supabase para resolver problemas de deploy.
    """
    logger.info("Forçando uso de SQLite local para deploy.")
    return conectar_db_sqlite()

# ------------- Função de teste de conexão (apenas para SQLite agora) -------------
def testar_conexao_sqlite():
    """Testa se consegue conectar no SQLite e listar tabelas."""
    try:
        conn = conectar_db_sqlite()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = [row[0] for row in cur.fetchall()]
        conn.close()

        logger.info(f"Conexão SQLite OK. Tabelas: {tabelas}")
        return True, f"Conexão OK. Tabelas encontradas: {tabelas}"

    except Exception as e:
        logger.error(f"Falha na conexão SQLite: {e}")
        return False, str(e)
