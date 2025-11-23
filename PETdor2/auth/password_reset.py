# PETdor2/auth/password_reset.py
import logging
from datetime import datetime, timedelta
import os
from database.connection import conectar_db
from auth.security import generate_reset_token, verify_reset_token, hash_password # Importa generate_reset_token e verify_reset_token
from utils.email_sender import enviar_email_recuperacao_senha # Nome da função corrigido
import streamlit as st # Para exibir mensagens de erro

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email):
    """
    Gera um token de redefinição de senha para o e-mail fornecido e envia um e-mail.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # 1. Buscar usuário por e-mail
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute("SELECT id, nome, email FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()

        if not usuario:
            logger.warning(f"Tentativa de reset de senha para e-mail não encontrado: {email}")
            return False, "Se o e-mail estiver registrado, um link de redefinição de senha foi enviado."

        # 2. Gerar token e data de expiração
        token = generate_reset_token(email)
        expires_at = datetime.now() + timedelta(hours=1) # Token válido por 1 hora

        # 3. Salvar token e expiração no banco de dados
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute(
            "UPDATE usuarios SET reset_password_token = %s, reset_password_expires = %s WHERE id = %s",
            (token, expires_at, usuario[0]) # usuario[0] é o id
        )
        conn.commit()
        logger.info(f"Token de reset de senha gerado e salvo para o usuário ID {usuario[0]}.")

        # 4. Enviar e-mail de redefinição
        reset_link = f"{os.getenv('STREAMLIT_APP_URL')}?action=reset_password&token={token}"
        email_enviado, email_msg = enviar_email_recuperacao_senha(usuario[2], usuario[1], reset_link) # email, nome, link

        if email_enviado:
            logger.info(f"E-mail de redefinição de senha enviado para {email}.")
            return True, "Se o e-mail estiver registrado, um link de redefinição de senha foi enviado."
        else:
            logger.error(f"Falha ao enviar e-mail de redefinição de senha para {email}: {email_msg}")
            # Mesmo que o e-mail falhe, o token foi gerado, então informamos ao usuário
            return True, "Seu link de redefinição foi gerado, mas houve um problema ao enviar o e-mail. Por favor, tente novamente ou use o token manualmente."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao solicitar redefinição de senha para {email}: {e}", exc_info=True)
        return False, f"Erro interno ao solicitar redefinição de senha: {e}"
    finally:
        if conn:
            conn.close()

def validar_token_reset(token):
    """
    Verifica se um token de redefinição de senha é válido e não expirou.
    Retorna (True, "Mensagem", email_do_usuario) ou (False, "Mensagem", None).
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # 1. Buscar usuário pelo token
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute(
            "SELECT email, reset_password_expires FROM usuarios WHERE reset_password_token = %s",
            (token,)
        )
        resultado = cur.fetchone()

        if not resultado:
            logger.warning(f"Tentativa de validação com token inválido: {token}")
            return False, "Token de redefinição inválido ou já utilizado.", None

        email_usuario = resultado[0]
        expires_at = resultado[1]

        # 2. Verificar expiração
        if expires_at and expires_at < datetime.now():
            logger.warning(f"Tentativa de validação com token expirado para {email_usuario}.")
            return False, "Token de redefinição expirado. Por favor, solicite um novo.", None

        logger.info(f"Token de reset de senha válido para {email_usuario}.")
        return True, "Token válido.", email_usuario

    except Exception as e:
        logger.error(f"Erro ao validar token de reset de senha: {e}", exc_info=True)
        return False, f"Erro interno ao validar token: {e}", None
    finally:
        if conn:
            conn.close()

def redefinir_senha_com_token(token, nova_senha):
    """
    Redefine a senha de um usuário usando um token válido.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # 1. Validar o token e obter o e-mail do usuário
        token_valido_status, msg_validacao, email_usuario = validar_token_reset(token)
        if not token_valido_status or not email_usuario:
            return False, msg_validacao

        # 2. Hash da nova senha
        senha_hash = hash_password(nova_senha)

        # 3. Atualizar senha e invalidar token
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute(
            "UPDATE usuarios SET senha_hash = %s, reset_password_token = NULL, reset_password_expires = NULL WHERE email = %s",
            (senha_hash, email_usuario)
        )
        conn.commit()
        logger.info(f"Senha redefinida com sucesso para {email_usuario}. Token invalidado.")
        return True, "Senha redefinida com sucesso. Você já pode fazer login."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao redefinir senha com token para {email_usuario}: {e}", exc_info=True)
        return False, f"Erro interno ao redefinir senha: {e}"
    finally:
        if conn:
            conn.close()
