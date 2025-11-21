# PETdor_2_0/database/connection.py
"""
Módulo de conexão com o banco de dados.
Atualmente configurado para usar SQLite localmente.
"""
import os
import sqlite3
import logging
# A classe 'namedtuple' não é mais necessária com sqlite3.Row

logger = logging.getLogger(__name__)

# --- SQLite (desenvolvimento local e fallback para produção) ---
def conectar_db_sqlite():
    """
    Conecta ao banco de dados SQLite local (petdor.db).
    Cria o diretório 'data' se não existir.
    Configura o row_factory para retornar linhas como objetos que se comportam como dicionários.
    """
    db_dir = "data"
    os.makedirs(db_dir, exist_ok=True) # Garante que o diretório 'data' existe
    db_path = os.path.join(db_dir, "petdor.db")

    # check_same_thread=False é importante para Streamlit, pois pode acessar o DB de threads diferentes
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row # Retorna linhas como objetos que se comportam como dicionários
    logger.info(f"Conectado ao SQLite: {db_path}")
    return conn

# --- Função principal de conexão ---
def conectar_db():
    """
    Função principal para conectar ao banco de dados.
    Atualmente força o uso de SQLite local.
    """
    logger.info("Forçando uso de SQLite local para deploy.")
    return conectar_db_sqlite()

# --- Função de teste de conexão (apenas para SQLite) ---
def testar_conexao_sqlite():
    """
    Testa se consegue conectar no SQLite e listar as tabelas existentes.
    Retorna True e uma mensagem de sucesso com as tabelas, ou False e a mensagem de erro.
    """
    conn = None # Inicializa conn como None para garantir que seja fechado no finally
    try:
        conn = conectar_db_sqlite()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = [row[0] for row in cur.fetchall()]

        logger.info(f"Conexão SQLite OK. Tabelas encontradas: {tabelas}")
        return True, f"Conexão OK. Tabelas encontradas: {tabelas}"

    except Exception as e:
        logger.error(f"Falha na conexão SQLite: {e}", exc_info=True) # Adicionado exc_info=True para logar o traceback completo
        return False, f"Falha na conexão SQLite: {e}"
    finally:
        if conn:
            conn.close() # Garante que a conexão seja fechada
