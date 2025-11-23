# PETdor2/auth/user.py
import logging
from datetime import datetime
import os
from database.connection import conectar_db
from .security import hash_password, generate_email_token, verify_email_token, verify_password
from utils.email_sender import enviar_email_confirmacao 
import uuid
import streamlit as st # Adicionado para st.error

logger = logging.getLogger(__name__)

# A função criar_tabelas_se_nao_existir não é mais necessária aqui,
# pois migrar_banco_completo() em database/migration.py já cuida disso.
# Se você ainda precisar de alguma lógica específica de tabela aqui,
# por favor, me avise.

def cadastrar_usuario(nome, email, senha, tipo_usuario, pais):
    """
    Cadastra um novo usuário no banco de dados (Supabase).
    Retorna True e mensagem de sucesso, ou False e mensagem de erro.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Verifica se o e-mail já existe
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            return False, "Este e-mail já está cadastrado."

        senha_hash = hash_password(senha)
        email_confirm_token = generate_email_token(email) # Gera token para o email

        cur.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """,
            (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Usuário {email} cadastrado com sucesso. ID: {user_id}")

        # Envia e-mail de confirmação
        # O link deve apontar para o seu app Streamlit com o token
        confirm_link = f"https://petdor.streamlit.app/?token={email_confirm_token}&action=confirm_email"
        ok_email, msg_email = enviar_email_confirmacao(email, nome, confirm_link)
        if not ok_email:
            logger.warning(f"Falha ao enviar e-mail de confirmação para {email}: {msg_email}")
            # Não impede o cadastro, mas informa o usuário
            return True, f"Cadastro realizado! No entanto, houve um problema ao enviar o e-mail de confirmação: {msg_email}. Por favor, verifique sua caixa de spam ou tente reenviar."

        return True, "Cadastro realizado com sucesso! Verifique seu e-mail para confirmar sua conta."

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao cadastrar usuário {email}: {e}", exc_info=True)
        return False, f"Erro ao cadastrar usuário: {e}"
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro inesperado ao cadastrar usuário {email}: {e}", exc_info=True)
        return False, f"Erro inesperado ao cadastrar usuário: {e}"
    finally:
        if conn:
            conn.close()

def verificar_credenciais(email, senha):
    """
    Verifica as credenciais do usuário.
    Retorna (True, user_data) se as credenciais forem válidas, (False, mensagem de erro) caso contrário.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor(cursor_factory=RealDictCursor) # Usa RealDictCursor para retornar dicionários

        cur.execute("SELECT id, nome, email, senha_hash, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "E-mail ou senha inválidos."

        if not verify_password(senha, usuario['senha_hash']):
            return False, "E-mail ou senha inválidos."

        if not usuario['email_confirmado']:
            return False, "Sua conta ainda não foi confirmada. Por favor, verifique seu e-mail."

        if not usuario['ativo']:
            return False, "Sua conta está desativada. Por favor, contate o suporte."

        # Remove o hash da senha antes de retornar os dados do usuário
        del usuario['senha_hash']
        return True, usuario

    except psycopg2.Error as e:
        logger.error(f"Erro ao verificar credenciais para {email}: {e}", exc_info=True)
        return False, f"Erro ao verificar credenciais: {e}"
    except Exception as e:
        logger.error(f"Erro inesperado ao verificar credenciais para {email}: {e}", exc_info=True)
        return False, f"Erro inesperado ao verificar credenciais: {e}"
    finally:
        if conn:
            conn.close()

def buscar_usuario_por_email(email):
    """Busca um usuário pelo e-mail."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, nome, email, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        return usuario
    except psycopg2.Error as e:
        logger.error(f"Erro ao buscar usuário por e-mail {email}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def confirmar_email(token):
    """Confirma o e-mail do usuário usando o token."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Busca o usuário pelo token
        cur.execute("SELECT id, email_confirm_token FROM usuarios WHERE email_confirm_token = %s", (token,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "Token de confirmação inválido ou expirado."

        # 2. Verifica a validade do token (se já não foi feito por verify_email_token)
        # Assumindo que verify_email_token já lida com expiração e validade
        token_valido, msg, email_do_token = verify_email_token(token)
        if not token_valido or email_do_token != usuario['email_confirm_token']: # Ajuste aqui se verify_email_token retorna o email
            return False, msg # Retorna a mensagem de erro da validação do token

        # 3. Atualiza o status de confirmação e remove o token
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
