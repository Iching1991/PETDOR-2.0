# PETdor_2_0/database/migration.py
import sqlite3
import os
from database.connection import conectar_db


USANDO_POSTGRES = bool(os.getenv("DB_HOST"))


# ==========================================================
# Criar tabelas da estrutura híbrida
# ==========================================================
def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()

    # -------------------------------
    # Tabela de Usuários
    # -------------------------------
    if USANDO_POSTGRES:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id BIGSERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT DEFAULT 'Brasil',

                email_confirmado BOOLEAN NOT NULL DEFAULT FALSE,
                email_confirm_token TEXT UNIQUE,

                reset_password_token TEXT UNIQUE,
                reset_password_expires TIMESTAMPTZ,

                ativo BOOLEAN NOT NULL DEFAULT TRUE,
                criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT DEFAULT 'Brasil',

                email_confirmado INTEGER DEFAULT 0,
                email_confirm_token TEXT,

                reset_password_token TEXT,
                reset_password_expires TIMESTAMP,

                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    # -------------------------------
    # LOG — Confirmação de E-mail
    # -------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_confirmacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expirado INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)

    # -------------------------------
    # LOG — Resets de Senha
    # -------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            utilizado INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)

    # -------------------------------
    # Tabela de Pets
    # -------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            idade INTEGER,
            peso REAL,
            tutor_id INTEGER NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tutor_id) REFERENCES usuarios(id)
        );
    """)

    # -------------------------------
    # Tabela de Avaliações
    # -------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            especie TEXT NOT NULL,
            respostas_json TEXT NOT NULL,
            pontuacao_total REAL NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)

    conn.commit()
    conn.close()
    print("✔ Banco atualizado: tabelas principais e de log criadas com sucesso.")


# ==========================================================
# Migração completa
# ==========================================================
def migrar_banco_completo():
    """
    Executa todas as migrações necessárias.
    Não reseta o banco automaticamente.
    """
    criar_tabelas()
    print("✔ Migração completa executada com sucesso.")


# ==========================================================
# Resetar banco (apenas desenvolvedor)
# ==========================================================
def resetar_banco():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS avaliacoes")
    cursor.execute("DROP TABLE IF EXISTS pets")
    cursor.execute("DROP TABLE IF EXISTS password_resets")
    cursor.execute("DROP TABLE IF EXISTS email_confirmacoes")
    cursor.execute("DROP TABLE IF EXISTS usuarios")

    conn.commit()
    conn.close()
    print("⚠ Banco resetado (DEV).")
