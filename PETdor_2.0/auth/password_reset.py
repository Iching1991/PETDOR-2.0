# PETdor_2_0/auth/password_reset.py
import streamlit as st
import logging
from datetime import datetime, timedelta
from database.connection import conectar_db
from .security import generate_reset_token, verify_reset_token
from utils.email_sender import enviar_email_reset_senha

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email: str):
    """
    Inicia o processo de redefinição de senha para o e-mail fornecido.
    Gera um token de reset e envia um e-mail ao usuário.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # CORREÇÃO: Usar '?' para placeholder do SQLite
        cur.execute("SELECT id, nome, email FROM usuarios WHERE email = ?", (email,))
        usuario = cur.fetchone()

        if not usuario:
            logger.warning(f"Tentativa de reset de senha para e-mail não encontrado: {email}")
            return False, "Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha."

        token = generate_reset_token()
        expira_em = datetime.now() + timedelta(hours=1) # Token válido por 1 hora

        # CORREÇÃO: Usar '?' para placeholders do SQLite
        cur.execute("""
            UPDATE usuarios
            SET reset_password_token = ?, reset_password_expires = ?
            WHERE id = ?
        """, (token, expira_em, usuario['id']))
        conn.commit()

        enviar_email_reset_senha(email, usuario['nome'], token)
        logger.info(f"Link de reset de senha enviado para {email}")
        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao solicitar reset de senha para {email}: {e}", exc_info=True)
        return False, f"Erro interno ao solicitar reset de senha: {e}"
    finally:
        if conn:
            conn.close()

def redefinir_senha_com_token(token: str, nova_senha: str):
    """
    Redefine a senha do usuário usando um token de reset válido.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # CORREÇÃO: Usar '?' para placeholders do SQLite
        cur.execute("""
            SELECT id, email, reset_password_expires
            FROM usuarios
            WHERE reset_password_token = ?
        """, (token,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "Token de redefinição de senha inválido ou expirado."

        # Verifica se o token expirou
        if usuario['reset_password_expires'] < datetime.now():
            # Limpa o token expirado para evitar reuso
            cur.execute("UPDATE usuarios SET reset_password_token = NULL, reset_password_expires = NULL WHERE id = ?", (usuario['id'],))
            conn.commit()
            return False, "Token de redefinição de senha expirado. Por favor, solicite um novo."

        # O token é válido, redefinir a senha
        from .user import redefinir_senha # Importação local para evitar circular

        sucesso, mensagem = redefinir_senha(usuario['email'], nova_senha)

        if sucesso:
            # Limpa o token após o uso bem-sucedido
            cur.execute("UPDATE usuarios SET reset_password_token = NULL, reset_password_expires = NULL WHERE id = ?", (usuario['id'],))
            conn.commit()
            logger.info(f"Senha redefinida com sucesso para {usuario['email']}")
            return True, "Senha redefinida com sucesso. Você já pode fazer login."
        else:
            return False, f"Erro ao redefinir senha: {mensagem}"

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao redefinir senha com token: {e}", exc_info=True)
        return False, f"Erro interno ao redefinir senha: {e}"
    finally:
        if conn:
            conn.close()
