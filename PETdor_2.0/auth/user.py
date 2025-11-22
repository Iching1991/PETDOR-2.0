# PETdor_2_0/auth/user.py
import logging
import os
from datetime import datetime, timedelta

from database.connection import conectar_db
from auth.security import hash_password, verify_password
from utils.email_sender import enviar_email_confirmacao
from utils.tokens import gerar_token_simples, validar_token_simples

logger = logging.getLogger(__name__)


# =====================================================
# AJUSTE AUTOMÁTICO DE PLACEHOLDER (SQLite ou PostgreSQL)
# =====================================================
def placeholder():
    """Retorna o placeholder correto dependendo do banco."""
    return "%s" if os.getenv("DB_HOST") else "?"


# =====================================================
# CRIAR TABELA SE NÃO EXISTIR
# =====================================================
def criar_tabelas_se_nao_existir():
    conn = conectar_db()
    cur = conn.cursor()

    if os.getenv("DB_HOST"):  # PostgreSQL
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
                reset_password_token TEXT,
                reset_password_expires TIMESTAMPTZ
            );
        """)
    else:  # SQLite
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT NOT NULL DEFAULT 'Brasil',
                email_confirm_token TEXT,
                email_confirmado INTEGER NOT NULL DEFAULT 0,
                ativo INTEGER NOT NULL DEFAULT 1,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reset_password_token TEXT,
                reset_password_expires TIMESTAMP
            );
        """)

    conn.commit()
    conn.close()


# =====================================================
# CADASTRAR USUÁRIO
# =====================================================
def cadastrar_usuario(nome, email, senha, tipo_usuario, pais):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        senha_hash = hash_password(senha)
        token = gerar_token_simples(email)

        sql = f"""
            INSERT INTO usuarios
            (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token, email_confirmado)
            VALUES ({placeholder()}, {placeholder()}, {placeholder()},
                    {placeholder()}, {placeholder()}, {placeholder()}, {placeholder()})
        """

        cur.execute(sql, (nome, email, senha_hash, tipo_usuario, pais, token, 0))
        conn.commit()

        logger.info(f"Usuário {email} cadastrado.")

        # Enviar confirmação
        if not enviar_email_confirmacao(email, nome, token):
            logger.error(f"Falha ao enviar e-mail de confirmação para {email}")
            return True, "Cadastro realizado, mas houve erro ao enviar o e-mail. Tente novamente depois."

        return True, "Cadastro realizado! Verifique seu e-mail para confirmar sua conta."

    except Exception as e:
        if conn:
            conn.rollback()
        if "UNIQUE constraint" in str(e) or "duplicate key" in str(e):
            return False, "Este e-mail já está cadastrado."
        logger.error(f"Erro ao cadastrar usuário: {e}", exc_info=True)
        return False, f"Erro ao cadastrar: {e}"

    finally:
        if conn:
            conn.close()


# =====================================================
# VERIFICAR LOGIN
# =====================================================
def verificar_credenciais(email, senha):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql = f"SELECT * FROM usuarios WHERE email = {placeholder()}"
        cur.execute(sql, (email,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "E-mail ou senha incorretos."

        if not usuario["email_confirmado"]:
            return False, "Confirme seu e-mail antes de entrar."

        if not usuario["ativo"]:
            return False, "Conta desativada."

        if verify_password(senha, usuario["senha_hash"]):
            return True, usuario

        return False, "E-mail ou senha incorretos."

    except Exception as e:
        logger.error(f"Erro no login: {e}", exc_info=True)
        return False, "Erro interno no servidor."

    finally:
        if conn:
            conn.close()


# =====================================================
# BUSCAR USUÁRIO POR E-MAIL
# =====================================================
def buscar_usuario_por_email(email):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql = f"SELECT * FROM usuarios WHERE email = {placeholder()}"
        cur.execute(sql, (email,))
        return cur.fetchone()

    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return None

    finally:
        if conn:
            conn.close()


# =====================================================
# CONFIRMAR E-MAIL
# =====================================================
def confirmar_email(token):
    email = validar_token_simples(token)
    if not email:
        return False, "Token inválido ou expirado."

    conn = conectar_db()
    cur = conn.cursor()

    sql = f"""
        UPDATE usuarios
        SET email_confirmado = 1,
            email_confirm_token = NULL
        WHERE email = {placeholder()}
    """

    cur.execute(sql, (email,))
    conn.commit()
    conn.close()

    return True, "E-mail confirmado com sucesso!"


# =====================================================
# REDEFINIR SENHA (USADO PELO RESET)
# =====================================================
def redefinir_senha(email, nova_senha):
    conn = conectar_db()
    cur = conn.cursor()

    senha_hash = hash_password(nova_senha)

    sql = f"UPDATE usuarios SET senha_hash = {placeholder()} WHERE email = {placeholder()}"
    cur.execute(sql, (senha_hash, email))

    conn.commit()
    conn.close()
    return True, "Senha alterada com sucesso."


# =====================================================
# LISTAR TODOS (ADMIN)
# =====================================================
def buscar_todos_usuarios():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, email, tipo_usuario, pais, email_confirmado, ativo, data_cadastro
        FROM usuarios
        ORDER BY data_cadastro DESC
    """)

    data = cur.fetchall()
    conn.close()
    return data


# =====================================================
# ATUALIZAR STATUS
# =====================================================
def atualizar_status_usuario(user_id, ativo):
    conn = conectar_db()
    cur = conn.cursor()

    sql = f"UPDATE usuarios SET ativo = {placeholder()} WHERE id = {placeholder()}"
    cur.execute(sql, (1 if ativo else 0, user_id))

    conn.commit()
    conn.close()
    return True, "Status atualizado."


# =====================================================
# ATUALIZAR TIPO
# =====================================================
def atualizar_tipo_usuario(user_id, tipo_usuario):
    conn = conectar_db()
    cur = conn.cursor()

    sql = f"UPDATE usuarios SET tipo_usuario = {placeholder()} WHERE id = {placeholder()}"
    cur.execute(sql, (tipo_usuario, user_id))

    conn.commit()
    conn.close()
    return True, "Tipo atualizado."
