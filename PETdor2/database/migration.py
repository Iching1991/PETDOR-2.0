# PETdor2/database/migration.py
import os
from .connection import conectar_db
import logging
import streamlit as st # Para exibir mensagens de erro no Streamlit

logger = logging.getLogger(__name__)

def migrar_banco_completo():
    """
    Executa todas as migrações necessárias para o banco de dados PostgreSQL (Supabase).
    Cria tabelas e colunas se não existirem.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # --- Tabela 'usuarios' ---
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

        # --- Tabela 'pets' ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                idade INTEGER,
                peso DECIMAL(5,2),
                genero TEXT,
                usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                data_cadastro TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        logger.info("Tabela 'pets' verificada/criada.")

        # --- Tabela 'avaliacoes' ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id SERIAL PRIMARY KEY,
                pet_id INTEGER REFERENCES pets(id) ON DELETE CASCADE,
                usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                data_avaliacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                pontuacao_total INTEGER NOT NULL,
                observacoes TEXT
            );
        """)
        logger.info("Tabela 'avaliacoes' verificada/criada.")

        # --- Tabela 'respostas_avaliacao' ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS respostas_avaliacao (
                id SERIAL PRIMARY KEY,
                avaliacao_id INTEGER REFERENCES avaliacoes(id) ON DELETE CASCADE,
                pergunta_id INTEGER NOT NULL, -- ID da pergunta (ex: 1, 2, 3...)
                resposta INTEGER NOT NULL,    -- Pontuação da resposta (ex: 0-7)
                data_resposta TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        logger.info("Tabela 'respostas_avaliacao' verificada/criada.")

        # --- Tabela 'especies' (para gerenciar configurações de espécies) ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS especies (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL UNIQUE,
                config_json JSONB NOT NULL -- Armazena a configuração da espécie em formato JSON
            );
        """)
        logger.info("Tabela 'especies' verificada/criada.")

        # --- Migração de colunas (se necessário) ---
        # Exemplo: Adicionar uma coluna 'telefone' à tabela 'usuarios' se ela não existir
        # cur.execute("""
        #     DO $$
        #     BEGIN
        #         IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='telefone') THEN
        #             ALTER TABLE usuarios ADD COLUMN telefone TEXT;
        #         END IF;
        #     END
        #     $$;
        # """)
        # logger.info("Coluna 'telefone' na tabela 'usuarios' verificada/adicionada.")

        conn.commit()
        logger.info("Migração do banco de dados PostgreSQL concluída com sucesso.")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro durante a migração do banco de dados PostgreSQL: {e}", exc_info=True)
        st.error(f"Erro crítico ao inicializar o banco de dados. Por favor, contate o suporte. Detalhes: {e}")
        st.stop() # Interrompe a execução do Streamlit app
    finally:
        if conn:
            conn.close()
