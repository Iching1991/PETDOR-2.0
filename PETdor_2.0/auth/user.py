# PETdor_2_0/auth/user.py
import logging
from datetime import datetime
import os
from database.connection import conectar_db
from .security import hash_password, generate_email_token, verify_email_token, verify_password
from ..utils.email_sender import enviar_email_confirmacao
import uuid

logger = logging.getLogger(__name__)

def criar_tabelas_se_nao_existir():
    conn = conectar_db()
    cur = conn.cursor()

    if os.getenv("DB_HOST"):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id BIGSERIAL PRIMARY KEY,
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
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT NOT NULL DEFAULT 'Brasil',
                email_confirm_token TEXT UNIQUE,
                email_confirmado BOOLEAN NOT NULL DEFAULT 0,
                ativo BOOLEAN NOT NULL DEFAULT 1,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reset_password_token TEXT UNIQUE,
                reset_password_expires TIMESTAMP
            );
        """)

    conn.commit()
    conn.close()


def cadastrar_usuario(nome, email, senha, tipo_usuario, pais):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        senha_hash = hash_password(senha)
        token = generate_email_token(email)

        cur.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token, email_confirmado)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (nome, email, senha_hash, tipo_usuario, pais, token))

        conn.commit()
        logger.info(f"Usuário {email} cadastrado com sucesso.")

        enviar_email_confirmacao(email, nome, token)

        return True, "Cadastro realizado com sucesso! Verifique seu e-mail."
    
    except Exception as e:
        if conn:
            conn.rollback()

        logger.error(f"Erro ao cadastrar usuário: {e}", exc_info=True)

        if "UNIQUE constraint failed: usuarios.email" in str(e):
            return False, "Este e-mail já está cadastrado."

        return False, f"Erro ao cadastrar usuário: {e}"

    finally:
        if conn:
            conn.close()


def verificar_credenciais(email, senha):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "E-mail ou senha incorretos."

        if usuario["email_confirmado"] == 0:
            return False, "Sua conta não foi confirmada."

        if usuario["ativo"] == 0:
            return False, "Conta desativada. Contate o suporte."

        if verify_password(senha, usuario["senha_hash"]):
            return True, usuario

        return False, "E-mail ou senha incorretos."

    except Exception as e:
        logger.error(f"Erro ao verificar credenciais: {e}", exc_info=True)
        return False, f"Erro interno: {e}"

    finally:
        if conn:
            conn.close()


def buscar_usuario_por_email(email):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cur.fetchone()

    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}", exc_info=True)
        return None

    finally:
        if conn:
            conn.close()


def confirmar_email(token):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        cur.execute("SELECT id FROM usuarios WHERE email_confirm_token = ? AND email_confirmado = 0", (token,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "Token inválido ou já utilizado."

        cur.execute("""
            UPDATE usuarios
            SET email_confirmado = 1, email_confirm_token = NULL
            WHERE id = ?
        """, (usuario["id"],))

        conn.commit()
        return True, "E-mail confirmado com sucesso."

    except Exception as e:
        if conn:
            conn.rollback()

        logger.error(f"Erro ao confirmar e-mail: {e}", exc_info=True)
        return False, f"Erro ao confirmar e-mail: {e}"

    finally:
        if conn:
            conn.close()


def redefinir_senha(email, nova_senha):
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        senha_hash = hash_password(nova_senha)

        cur.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (senha_hash, email))
        conn.commit()

        return True, "Senha redefinida com sucesso."

    except Exception as e:
        if conn:
            conn.rollback()

        return False, f"Erro ao redefinir senha: {e}"

    finally:
        if conn:
            conn.close()

