# PETdor2/database/connection.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor # Para retornar resultados como dicionários
import logging

logger = logging.getLogger(__name__)

def conectar_db():
    """
    Estabelece uma conexão com o banco de dados PostgreSQL (Supabase).
    Retorna o objeto de conexão.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432") # Porta padrão do PostgreSQL
        )
        # Configura o cursor para retornar resultados como dicionários
        # Isso é similar ao sqlite3.Row, mas para psycopg2
        conn.cursor_factory = RealDictCursor 
        logger.info("Conexão com o banco de dados PostgreSQL estabelecida com sucesso.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados PostgreSQL: {e}", exc_info=True)
        st.error(f"Erro ao conectar ao banco de dados. Por favor, tente novamente mais tarde. Detalhes: {e}")
        st.stop() # Interrompe a execução do Streamlit app
    except Exception as e:
        logger.error(f"Erro inesperado ao conectar ao banco de dados: {e}", exc_info=True)
        st.error(f"Erro inesperado ao conectar ao banco de dados. Detalhes: {e}")
        st.stop() # Interrompe a execução do Streamlit app

# Removendo a função criar_diretorio_db, pois não é mais necessária para PostgreSQL
# def criar_diretorio_db():
#     # ... (código anterior removido)
