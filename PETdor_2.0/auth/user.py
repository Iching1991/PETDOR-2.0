# PETdor_2_0/auth/user.py
import streamlit as st
import logging
from datetime import datetime
import os # Importado para usar os.getenv na criar_tabelas_se_nao_existir
from database.connection import conectar_db # Importa a função inteligente
from .security import hash_password, generate_email_token, verify_email_token, verify_password # Adicionado verify_password
from utils.email_sender import enviar_email_confirmacao # Importação ABSOLUTA corrigida
import uuid # Mantido, embora generate_email_token já use internamente

logger = logging.getLogger(__name__)

def criar_tabelas_se_nao_existir():
    """Cria a tabela de usuários se não existir (para SQLite local ou como fallback)."""
    conn = conectar_db()
    cur = conn.cursor()
    # Note: O script de criação de tabelas já foi rodado no Supabase.
    # Esta função é mais para garantir compatibilidade local ou para novas tabelas.
    # Para o Supabase, as tabelas já existem.
    # Usar BIGSERIAL para PostgreSQL e INTEGER PRIMARY KEY AUTOINCREMENT para SQLite
    if os.getenv("DB_HOST"): # Se estiver no Supabase (PostgreSQL)
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
                email_confirmado BOOLEAN NOT NULL DEFAULT FALSE,
                ativo BOOLEAN NOT NULL DEFAULT TRUE,
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
        token = generate_email_token()

        # Usar %s para PostgreSQL e FALSE para booleano
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token, email_confirmado)
            VALUES (%s, %s, %s, %s, %s, %s, FALSE)
        """, (nome, email, senha_hash, tipo_usuario, pais, token))

        conn.commit()
        logger.info(f"Usuário {email} cadastrado com sucesso.")

        # Enviar e-mail de confirmação (nome da função corrigido)
        enviar_email_confirmacao(email, nome, token)

        return True, "Cadastro realizado com sucesso! Verifique seu e-mail para confirmar a conta."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao cadastrar usuário: {e}")
        # Se for erro de UNIQUE constraint, dar uma mensagem mais amigável
        if "UNIQUE constraint failed: usuarios.email" in str(e) or "duplicate key value violates unique constraint" in str(e):
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
        # Usar %s para PostgreSQL
        cur.execute("SELECT id, nome, email, senha_hash, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()

        # Usar verify_password para verificar a senha
        if usuario and usuario['ativo'] and usuario['email_confirmado'] and verify_password(senha, usuario['senha_hash']):
            logger.info(f"Login bem-sucedido para {email}")
            return True, usuario
        elif usuario and not usuario['email_confirmado']:
            return False, "Sua conta ainda não foi confirmada. Verifique seu e-mail."
        elif usuario and not usuario['ativo']:
            return False, "Sua conta está inativa. Entre em contato com o suporte."
        else:
            logger.warning(f"Falha no login para {email}")
            return False, "E-mail ou senha incorretos."
    except Exception as e:
        logger.error(f"Erro ao verificar credenciais: {e}")
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
        cur.execute("SELECT id, nome, email, senha_hash, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        return usuario
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por e-mail: {e}")
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
        cur.execute("SELECT id FROM usuarios WHERE email_confirm_token = %s AND email_confirmado = FALSE", (token,))
        usuario = cur.fetchone()

        if usuario:
            # Atualiza o status de confirmação e remove o token
            cur.execute("""
                UPDATE usuarios
                SET email_confirmado = TRUE, email_confirm_token = NULL
                WHERE id = %s
            """, (usuario['id'],))
            conn.commit()
            logger.info(f"E-mail confirmado para o usuário ID: {usuario['id']}")
            return True, "Seu e-mail foi confirmado com sucesso! Você já pode fazer login."
        else:
            return False, "Token de confirmação inválido ou já utilizado."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao confirmar e-mail: {e}")
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
        cur.execute("UPDATE usuarios SET senha_hash = %s WHERE email = %s", (senha_hash, email))
        conn.commit()
        logger.info(f"Senha redefinida para {email}")
        return True, "Senha redefinida com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao redefinir senha para {email}: {e}")
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
        logger.error(f"Erro ao buscar todos os usuários: {e}")
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
        cur.execute("UPDATE usuarios SET ativo = %s WHERE id = %s", (ativo, user_id))
        conn.commit()
        logger.info(f"Status do usuário ID {user_id} atualizado para ativo={ativo}")
        return True, "Status atualizado com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao atualizar status do usuário ID {user_id}: {e}")
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
        cur.execute("UPDATE usuarios SET tipo_usuario = %s WHERE id = %s", (tipo_usuario, user_id))
        conn.commit()
        logger.info(f"Tipo do usuário ID {user_id} atualizado para {tipo_usuario}")
        return True, "Tipo de usuário atualizado com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao atualizar tipo do usuário ID {user_id}: {e}")
        return False, f"Erro ao atualizar tipo de usuário: {e}"
    finally:
        if conn:
            conn.close()
