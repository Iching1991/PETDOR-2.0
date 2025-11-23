# PETdor2/database/migration.py
import logging
import streamlit as st
from database.supabase_client import supabase_table_select, supabase_table_insert

logger = logging.getLogger(__name__)

def migrar_banco_completo():
    """
    Cria/verifica tabelas necessárias no Supabase de forma segura.
    """
    if supabase is None:
        logger.error("Supabase não inicializado. Migração não pode ser executada.")
        st.error("Supabase não inicializado. Contate o administrador.")
        st.stop()
        return

    tabelas_sql = {
        "usuarios": """
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT NOT NULL DEFAULT 'Brasil',
                email_confirm_token TEXT UNIQUE,
                email_confirmado BOOLEAN NOT NULL DEFAULT FALSE,
                ativo BOOLEAN NOT NULL DEFAULT TRUE,
                data_cadastro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                reset_password_token TEXT UNIQUE,
                reset_password_expires TIMESTAMPTZ
            );
        """,
        "pets": """
            CREATE TABLE IF NOT EXISTS pets (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                data_nascimento DATE,
                id_usuario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                data_cadastro TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """,
        "avaliacoes": """
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id SERIAL PRIMARY KEY,
                id_pet INTEGER REFERENCES pets(id) ON DELETE CASCADE,
                data_avaliacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                pontuacao_total INTEGER NOT NULL,
                observacoes TEXT
            );
        """,
        "backups": """
            CREATE TABLE IF NOT EXISTS backups (
                id SERIAL PRIMARY KEY,
                nome_arquivo TEXT NOT NULL,
                data_backup TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                tamanho_bytes INTEGER,
                caminho_armazenamento TEXT
            );
        """
    }

    for nome_tabela, sql in tabelas_sql.items():
        try:
            response = supabase.rpc("exec_sql", {"query": sql}).execute()
            if response.error:
                logger.error(f"Erro ao criar/verificar tabela {nome_tabela}: {response.error.message}")
                st.warning(f"Falha ao criar/verificar tabela {nome_tabela}: {response.error.message}")
            else:
                logger.info(f"Tabela {nome_tabela} criada/verificada com sucesso.")
        except Exception as e:
            logger.error(f"Exceção ao criar/verificar tabela {nome_tabela}: {e}", exc_info=True)
            st.warning(f"Erro ao criar/verificar tabela {nome_tabela}: {e}")

    logger.info("Migração do banco de dados concluída.")

