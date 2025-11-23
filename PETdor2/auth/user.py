# PETdor2/auth/user.py
import logging
from datetime import datetime
import os
from database.connection import conectar_db
from auth.security import hash_password, generate_email_token, verify_email_token, verify_password
from utils.email_sender import enviar_email_confirmacao 
import uuid
import streamlit as st # Para exibir mensagens de erro
import psycopg2 # Para capturar erros específicos do psycopg2
from psycopg2.extras import RealDictCursor # Para buscar resultados como dicionários

logger = logging.getLogger(__name__)

# A função criar_tabelas_se_nao_existir foi movida para database/migration.py

def cadastrar_usuario(nome: str, email: str, senha: str, tipo_usuario: str = 'Tutor', pais: str = 'Brasil') -> tuple[bool, str]:
    """
    Cadastra um novo usuário no banco de dados.
    Retorna (True, "Mensagem de sucesso") ou (False, "Mensagem de erro").
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # 1. Verificar se o e-mail já existe
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            return False, "Este e-mail já está cadastrado."

        # 2. Gerar hash da senha
        senha_hash = hash_password(senha)

        # 3. Gerar token de confirmação de e-mail
        email_confirm_token = generate_email_token(email)

        # 4. Inserir usuário
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Usuário {email} cadastrado com sucesso com ID {user_id}.")

        # 5. Enviar e-mail de confirmação
        ok_email, msg_email = enviar_email_confirmacao(email, email_confirm_token)
        if not ok_email:
            logger.error(f"Falha ao enviar e-mail de confirmação para {email}: {msg_email}")
            # Não impede o cadastro, mas informa o erro
            return True, f"Cadastro realizado, mas houve um erro ao enviar o e-mail de confirmação: {msg_email}. Por favor, tente reenviar a confirmação mais tarde."

        return True, "Cadastro realizado com sucesso! Verifique seu e-mail para confirmar sua conta."

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro de banco de dados ao cadastrar usuário {email}: {e}", exc_info=True)
        return False, f"Erro ao cadastrar usuário: {e}"
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado ao cadastrar usuário {email}: {e}", exc_info=True)
        return False, f"Erro inesperado ao cadastrar usuário: {e}"
    finally:
        if conn:
            conn.close()

def verificar_credenciais(email: str, senha: str) -> tuple[bool, str | dict]:
    """
    Verifica as credenciais do usuário.
    Retorna (True, dados_do_usuario) ou (False, "Mensagem de erro").
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor(cursor_factory=RealDictCursor) # Retorna como dicionário

        cur.execute("SELECT id, nome, email, senha_hash, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "E-mail ou senha incorretos."

        if not verify_password(senha, usuario["senha_hash"]):
            return False, "E-mail ou senha incorretos."

        if not usuario["email_confirmado"]:
            return False, "Sua conta ainda não foi confirmada. Verifique seu e-mail."

        if not usuario["ativo"]:
            return False, "Sua conta está inativa. Por favor, contate o suporte."

        # Remove o hash da senha antes de retornar os dados do usuário
        del usuario["senha_hash"]
        return True, usuario

    except psycopg2.Error as e:
        logger.error(f"Erro de banco de dados ao verificar credenciais para {email}: {e}", exc_info=True)
        return False, f"Erro ao verificar credenciais: {e}"
    except Exception as e:
        logger.error(f"Erro inesperado ao verificar credenciais para {email}: {e}", exc_info=True)
        return False, f"Erro inesperado ao verificar credenciais: {e}"
    finally:
        if conn:
            conn.close()

def buscar_usuario_por_email(email: str) -> dict | None:
    """Busca um usuário pelo e-mail e retorna seus dados como dicionário."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, nome, email, senha_hash, tipo_usuario, email_confirm_token, email_confirmado, ativo, data_cadastro, reset_password_token, reset_password_expires FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        return usuario
    except psycopg2.Error as e:
        logger.error(f"Erro ao buscar usuário por e-mail {email}: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar usuário por e-mail {email}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def confirmar_email(token: str) -> tuple[bool, str]:
    """
    Confirma o e-mail de um usuário usando um token.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        email_do_token = verify_email_token(token)
        if not email_do_token:
            return False, "Token de confirmação inválido ou expirado."

        usuario = buscar_usuario_por_email(email_do_token)
        if not usuario:
            return False, "Usuário não encontrado para este token."

        if usuario["email_confirmado"]:
            return True, "Seu e-mail já foi confirmado anteriormente."

        # Atualiza o status de confirmação e remove o token
        cur.execute(
            "UPDATE usuarios SET email_confirmado = TRUE, email_confirm_token = NULL WHERE id = %s",
            (usuario["id"],)
        )
        conn.commit()
        logger.info(f"E-mail {email_do_token} confirmado com sucesso.")
        return True, "E-mail confirmado com sucesso."
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao confirmar e-mail com token {token}: {e}", exc_info=True)
        return False, f"Erro ao confirmar e-mail: {e}"
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado ao confirmar e-mail com token {token}: {e}", exc_info=True)
        return False, f"Erro inesperado ao confirmar e-mail: {e}"
    finally:
        if conn:
            conn.close()

def redefinir_senha(email, nova_senha):
    """
    Redefine a senha de um usuário (esta função pode ser chamada após a validação do token).
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        senha_hash = hash_password(nova_senha)
        cur.execute("UPDATE usuarios SET senha_hash = %s WHERE email = %s", (senha_hash, email))
        conn.commit()
        logger.info(f"Senha redefinida para {email}")
        return True, "Senha redefinida com sucesso."
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao redefinir senha para {email}: {e}", exc_info=True)
        return False, f"Erro ao redefinir senha: {e}"
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado ao redefinir senha para {email}: {e}", exc_info=True)
        return False, f"Erro inesperado ao redefinir senha: {e}"
    finally:
        if conn:
            conn.close()

def buscar_todos_usuarios():
    """Retorna todos os usuários (para fins administrativos)."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, nome, email, tipo_usuario, pais, email_confirmado, ativo, data_cadastro FROM usuarios ORDER BY data_cadastro DESC")
        usuarios = cur.fetchall()
        return usuarios
    except psycopg2.Error as e:
        logger.error(f"Erro ao buscar todos os usuários: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar todos os usuários: {e}", exc_info=True)
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
        cur.execute("UPDATE usuarios SET ativo = %s WHERE id = %s", (ativo, user_id)) # PostgreSQL usa TRUE/FALSE
        conn.commit()
        logger.info(f"Status do usuário ID {user_id} atualizado para ativo={ativo}")
        return True, "Status atualizado com sucesso."
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao atualizar status do usuário ID {user_id}: {e}", exc_info=True)
        return False, f"Erro ao atualizar status: {e}"
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado ao atualizar status do usuário ID {user_id}: {e}", exc_info=True)
        return False, f"Erro inesperado ao atualizar status: {e}"
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
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao atualizar tipo do usuário ID {user_id}: {e}", exc_info=True)
        return False, f"Erro ao atualizar tipo de usuário: {e}"
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado ao atualizar tipo do usuário ID {user_id}: {e}", exc_info=True)
        return False, f"Erro inesperado ao atualizar tipo de usuário: {e}"
    finally:
        if conn:
            conn.close()
