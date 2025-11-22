# PETdor_2_0/auth/user.py
import streamlit as st
import logging
from datetime import datetime
import os
from database.connection import conectar_db
from .security import hash_password, generate_email_token, verify_email_token, verify_password
from utils.email_sender import enviar_email_confirmacao
import uuid

logger = logging.getLogger(__name__)

def criar_tabelas_se_nao_existir():
    """Cria a tabela de usuários se não existir (para SQLite local ou como fallback)."""
    conn = conectar_db()
    cur = conn.cursor()

    # Nota: A lógica de criação de tabelas aqui ainda está dividida por DB_HOST.
    # Como estamos forçando SQLite, a parte do PostgreSQL não será executada.
    # Para o SQLite, os tipos de dados e defaults estão corretos.

    # A verificação de os.getenv("DB_HOST") é para o caso de um dia você voltar a usar Supabase.
    # Por enquanto, o conectar_db() sempre retorna uma conexão SQLite.
    if os.getenv("DB_HOST"): # Se estivesse no Supabase (PostgreSQL)
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
    else: # Se estiver no ambiente local (SQLite)
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

        # CORREÇÃO: Usar '?' para placeholders do SQLite e 0 para FALSE
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token, email_confirmado)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (nome, email, senha_hash, tipo_usuario, pais, token))

        conn.commit()
        logger.info(f"Usuário {email} cadastrado com sucesso.")

        # Enviar e-mail de confirmação
        enviar_email_confirmacao(email, nome, token)

        return True, "Cadastro realizado com sucesso! Verifique seu e-mail para confirmar a conta."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao cadastrar usuário: {e}", exc_info=True) # Adicionado exc_info para log mais detalhado

        # Se for erro de UNIQUE constraint, dar uma mensagem mais amigável
        if "UNIQUE constraint failed: usuarios.email" in str(e): # Mensagem específica do SQLite
            return False, "Este e-mail já está cadastrado. Tente fazer login ou redefinir a senha."
        # Manter a verificação para PostgreSQL caso a lógica de DB_HOST seja reativada no futuro
        elif "duplicate key value violates unique constraint" in str(e):
            return False, "Este e-mail já está cadastrado. Tente fazer login ou redefinir a senha."

        return False, f"Erro ao cadastrar usuário: {e}"
    finally:
        if conn:
            conn.close()

def verificar_credenciais(email, senha):
    """Verifica as credenciais do usuário."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # CORREÇÃO: Usar '?' para placeholders do SQLite
        cur.execute("SELECT id, nome, email, senha_hash, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = ?", (email,))
        usuario = cur.fetchone()

        # SQLite retorna 0/1 para BOOLEAN, então a comparação é direta
        if usuario and usuario['ativo'] == 1 and usuario['email_confirmado'] == 1 and verify_password(senha, usuario['senha_hash']):
            logger.info(f"Login bem-sucedido para {email}")
            return True, usuario
        elif usuario and usuario['email_confirmado'] == 0:
            return False, "Sua conta ainda não foi confirmada. Verifique seu e-mail."
        elif usuario and usuario['ativo'] == 0:
            return False, "Sua conta está inativa. Entre em contato com o suporte."
        else:
            logger.warning(f"Falha no login para {email}")
            return False, "E-mail ou senha incorretos."
    except Exception as e:
        logger.error(f"Erro ao verificar credenciais: {e}", exc_info=True)
        return False, f"Erro interno ao verificar credenciais: {e}"
    finally:
        if conn:
            conn.close()

def buscar_usuario_por_email(email):
    """Busca um usuário pelo e-mail."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # CORREÇÃO: Usar '?' para placeholders do SQLite
        cur.execute("SELECT id, nome, email, senha_hash, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = ?", (email,))
        usuario = cur.fetchone()
        return usuario
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por e-mail: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def confirmar_email(token):
    """Confirma o e-mail do usuário usando o token."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # Primeiro, verifica se o token existe e não está confirmado
        # CORREÇÃO: Usar '?' para placeholders do SQLite e 0 para FALSE
        cur.execute("SELECT id FROM usuarios WHERE email_confirm_token = ? AND email_confirmado = 0", (token,))
        usuario = cur.fetchone()
        if usuario:
            # Atualiza o status de confirmação e remove o token
            # CORREÇÃO: Usar '?' para placeholders do SQLite e 1 para TRUE
            cur.execute("""
                UPDATE usuarios
                SET email_confirmado = 1, email_confirm_token = NULL
                WHERE id = ?
            """, (usuario['id'],))
            conn.commit()
            logger.info(f"E-mail confirmado para o usuário ID: {usuario['id']}")
            return True, "Seu e-mail foi confirmado com sucesso! Você já pode fazer login."
        else:
            return False, "Token de confirmação inválido ou já utilizado."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao confirmar e-mail: {e}", exc_info=True)
        return False, f"Erro interno ao confirmar e-mail: {e}"
    finally:
        if conn:
            conn.close()

def redefinir_senha(email, nova_senha):
    """Redefine a senha de um usuário."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        senha_hash = hash_password(nova_senha)
        # CORREÇÃO: Usar '?' para placeholders do SQLite
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
        # CORREÇÃO: Nenhuma alteração de placeholder, mas a query está ok para SQLite
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
        # CORREÇÃO: Usar '?' para placeholders do SQLite e 0/1 para booleano
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
        # CORREÇÃO: Usar '?' para placeholders do SQLite
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

