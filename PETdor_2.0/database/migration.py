import sqlite3
from .connection import conectar_db # Importação relativa, mais robusta dentro do pacote

# ==========================================================
# Função principal para criar todas as tabelas
# ==========================================================
def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()

    # -------------------------------
    # Tabela de usuários
    # -------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL,              -- tutor, veterinario, clinica
            pais TEXT,
            email_confirmado INTEGER DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # -------------------------------
    # Tokens de confirmação de e-mail
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
    # Tokens de recuperação de senha
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
    print("✔ Banco atualizado: Todas as tabelas foram criadas com sucesso.")


# ==========================================================
# Migração completa (ponto único de entrada para migrações)
# ==========================================================
def migrar_banco_completo():
    """
    Executa todas as migrações necessárias para deixar o banco atualizado.

    No momento:
    - Cria as tabelas, se não existirem (criar_tabelas).

    Futuras migrações (ex: novas colunas, flags de desativação, etc.)
    podem ser adicionadas aqui em sequência.
    """
    criar_tabelas()
    print("✔ Migração completa executada (criação/atualização de tabelas).")


# ==========================================================
# Utilitário opcional para resetar o banco (apenas dev)
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
    print("⚠ Banco de dados resetado (modo DEV).")
