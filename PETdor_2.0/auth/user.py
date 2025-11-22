# PETdor_2_0/auth/user.py
import logging
from datetime import datetime
import os
from database.connection import conectar_db
from .security import hash_password, generate_email_token, verify_email_token, verify_password
# CORREÇÃO: Alterar importação relativa para absoluta
from PETdor_2_0.utils.email_sender import enviar_email_confirmacao
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
                email_confirmado BOOLEAN NOT NULL DEFAULT 0, -- SQLite usa 0/1 para BOOLEAN
                ativo BOOLEAN NOT NULL DEFAULT 1,           -- SQLite usa 0/1 para BOOLEAN
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reset_password_token TEXT UNIQUE,
                reset_password_expires TIMESTAMP
            );
        """)
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, email, senha, tipo_usuario, pais):
    """
    Cadastra um novo usuário no banco de dados.
    Retorna True e mensagem de sucesso, ou False e mensagem de erro.
    """
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

        enviado = enviar_email_confirmacao(email, nome, token)
        if not enviado:
            logger.error(f"Falha ao enviar e-mail de confirmação para {email}")
            return True, "Cadastro realizado com sucesso! No entanto, houve um problema ao enviar o e-mail de confirmação. Por favor, tente confirmar mais tarde."

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
        logger.info(f"Senha redefinida para {email}")
        return True, "Senha redefinida com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao redefinir senha para {email}: {e}", exc_info=True)
        return False, f"Erro ao redefinir senha: {e}"
    finally:
        if conn:
            conn.close()

def buscar_todos_usuarios():
    """Retorna todos os usuários (para fins administrativos)."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, email, tipo_usuario, pais, email_confirmado, ativo, data_cadastro FROM usuarios ORDER BY data_cadastro DESC")
        usuarios = cur.fetchall()
        return usuarios
    except Exception as e:
        logger.error(f"Erro ao buscar todos os usuários: {e}", exc_info=True)
        return []
    finally:
        if conn:
            conn.close()

def atualizar_status_usuario(user_id, ativo):
    """Ativa ou desativa um usuário."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET ativo = ? WHERE id = ?", (1 if ativo else 0, user_id))
        conn.commit()
        logger.info(f"Status do usuário ID {user_id} atualizado para ativo={ativo}")
        return True, "Status atualizado com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao atualizar status do usuário ID {user_id}: {e}", exc_info=True)
        return False, f"Erro ao atualizar status: {e}"
    finally:
        if conn:
            conn.close()

def atualizar_tipo_usuario(user_id, tipo_usuario):
    """Atualiza o tipo de usuário."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET tipo_usuario = ? WHERE id = ?", (tipo_usuario, user_id))
        conn.commit()
        logger.info(f"Tipo do usuário ID {user_id} atualizado para {tipo_usuario}")
        return True, "Tipo de usuário atualizado com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao atualizar tipo do usuário ID {user_id}: {e}", exc_info=True)
        return False, f"Erro ao atualizar tipo de usuário: {e}"
    finally:
        if conn:
            conn.close()

