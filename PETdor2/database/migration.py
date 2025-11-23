# PETdor2/database/migration.py
import logging
from database.connection import conectar_db
import streamlit as st # Para exibir mensagens de erro no Streamlit
import psycopg2 # Para capturar erros específicos do psycopg2

logger = logging.getLogger(__name__)

def migrar_banco_completo():
    """
    Cria todas as tabelas necessárias no banco de dados PostgreSQL (Supabase)
    se elas ainda não existirem.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Tabela de usuários
        cur.execute("""
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
        """)
        logger.info("Tabela 'usuarios' verificada/criada.")

        # Tabela de pets (exemplo, ajuste conforme seu modelo de dados)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                data_nascimento DATE,
                id_usuario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                data_cadastro TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        logger.info("Tabela 'pets' verificada/criada.")

        # Tabela de avaliações (exemplo, ajuste conforme seu modelo de dados)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id SERIAL PRIMARY KEY,
                id_pet INTEGER REFERENCES pets(id) ON DELETE CASCADE,
                data_avaliacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                pontuacao_total INTEGER NOT NULL,
                observacoes TEXT
            );
        """)
        logger.info("Tabela 'avaliacoes' verificada/criada.")

        # Tabela de backups (conforme sua memória)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id SERIAL PRIMARY KEY,
                nome_arquivo TEXT NOT NULL,
                data_backup TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                tamanho_bytes INTEGER,
                caminho_armazenamento TEXT
            );
        """)
        logger.info("Tabela 'backups' verificada/criada.")

        # --- Migrações de Colunas (se necessário) ---
        # Exemplo: Adicionar coluna 'ativo' se não existir
        try:
            cur.execute("ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;")
            conn.commit()
            logger.info("Coluna 'ativo' adicionada à tabela 'usuarios'.")
        except psycopg2.errors.DuplicateColumn:
            conn.rollback() # Rollback da transação se a coluna já existe
            logger.info("Coluna 'ativo' já existe na tabela 'usuarios'.")
        except Exception as e:
            conn.rollback()
            logger.warning(f"Erro ao adicionar coluna 'ativo': {e}")

        # Exemplo: Adicionar coluna 'email_confirmado' se não existir
        try:
            cur.execute("ALTER TABLE usuarios ADD COLUMN email_confirmado BOOLEAN NOT NULL DEFAULT FALSE;")
            conn.commit()
            logger.info("Coluna 'email_confirmado' adicionada à tabela 'usuarios'.")
        except psycopg2.errors.DuplicateColumn:
            conn.rollback()
            logger.info("Coluna 'email_confirmado' já existe na tabela 'usuarios'.")
        except Exception as e:
            conn.rollback()
            logger.warning(f"Erro ao adicionar coluna 'email_confirmado': {e}")

        # Exemplo: Adicionar coluna 'reset_password_token' se não existir
        try:
            cur.execute("ALTER TABLE usuarios ADD COLUMN reset_password_token TEXT UNIQUE;")
            conn.commit()
            logger.info("Coluna 'reset_password_token' adicionada à tabela 'usuarios'.")
        except psycopg2.errors.DuplicateColumn:
            conn.rollback()
            logger.info("Coluna 'reset_password_token' já existe na tabela 'usuarios'.")
        except Exception as e:
            conn.rollback()
            logger.warning(f"Erro ao adicionar coluna 'reset_password_token': {e}")

        # Exemplo: Adicionar coluna 'reset_password_expires' se não existir
        try:
            cur.execute("ALTER TABLE usuarios ADD COLUMN reset_password_expires TIMESTAMPTZ;")
            conn.commit()
            logger.info("Coluna 'reset_password_expires' adicionada à tabela 'usuarios'.")
        except psycopg2.errors.DuplicateColumn:
            conn.rollback()
            logger.info("Coluna 'reset_password_expires' já existe na tabela 'usuarios'.")
        except Exception as e:
            conn.rollback()
            logger.warning(f"Erro ao adicionar coluna 'reset_password_expires': {e}")

        conn.commit()
        logger.info("Migração do banco de dados concluída com sucesso.")

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro de banco de dados durante a migração: {e}", exc_info=True)
        st.error(f"Erro crítico ao inicializar o banco de dados. Por favor, contate o suporte. Detalhes: {e}")
        st.stop()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado durante a migração do banco de dados: {e}", exc_info=True)
        st.error(f"Erro inesperado ao inicializar o banco de dados. Detalhes: {e}")
        st.stop()
    finally:
        if conn:
            conn.close()
