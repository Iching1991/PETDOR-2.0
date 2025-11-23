# PETdor2/database/migration.py
import logging
from database.connection import conectar_db
import streamlit as st # Para exibir mensagens de erro no Streamlit

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

        conn.commit()
        logger.info("Migração de banco de dados concluída com sucesso para Supabase.")

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro na migração do banco de dados (Supabase): {e}", exc_info=True)
        st.error(f"Erro crítico na inicialização do banco de dados. Por favor, contate o suporte. Detalhes: {e}")
        st.stop()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado na migração do banco de dados: {e}", exc_info=True)
        st.error(f"Erro inesperado na inicialização do banco de dados. Detalhes: {e}")
        st.stop()
    finally:
        if conn:
            conn.close()

# Função para migrar colunas de desativação (se necessário, adapte para PostgreSQL)
def migrar_colunas_desativacao():
    """
    Adiciona colunas 'ativo' e 'email_confirmado' à tabela 'usuarios' se não existirem.
    (Esta função pode ser integrada diretamente na migração completa ou chamada separadamente).
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Verifica e adiciona 'ativo'
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='ativo') THEN
                    ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
                END IF;
            END
            $$;
        """)
        logger.info("Coluna 'ativo' na tabela 'usuarios' verificada/adicionada.")

        # Verifica e adiciona 'email_confirmado'
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='email_confirmado') THEN
                    ALTER TABLE usuarios ADD COLUMN email_confirmado BOOLEAN NOT NULL DEFAULT FALSE;
                END IF;
            END
            $$;
        """)
        logger.info("Coluna 'email_confirmado' na tabela 'usuarios' verificada/adicionada.")

        conn.commit()
        logger.info("Migração de colunas de desativação concluída.")

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro na migração de colunas de desativação (Supabase): {e}", exc_info=True)
        st.error(f"Erro na migração de colunas. Detalhes: {e}")
        st.stop()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado na migração de colunas: {e}", exc_info=True)
        st.error(f"Erro inesperado na migração de colunas. Detalhes: {e}")
        st.stop()
    finally:
        if conn:
            conn.close()
