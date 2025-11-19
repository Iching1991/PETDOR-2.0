"""
Sistema de recuperação de senha do PETDor
"""
import logging
from database.connection import conectar_db
from utils.tokens import gerar_token_simples, validar_token_simples
from utils.email_sender import enviar_email_recuperacao_senha
from auth.security import gerar_hash_senha

logger = logging.getLogger(__name__)


# -------------------------------------------------
# 1) Enviar e-mail com token de reset
# -------------------------------------------------

def solicitar_reset_senha(email):
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome FROM usuarios WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return True  # não revela se existe ou não

        usuario_id, nome = row
        token = gerar_token_simples()

        cursor.execute("""
            INSERT INTO reset_senhas (usuario_id, token)
            VALUES (?, ?)
        """, (usuario_id, token))

        conn.commit()
        conn.close()

        link = f"https://petdor.streamlit.app/reset_senha?token={token}"

        assunto = "Redefinição de Senha - PETDor"
        mensagem = f"""
Olá, {nome}!

Recebemos uma solicitação para redefinir sua senha.

Use o link abaixo para prosseguir:

🔗 {link}

Se você não solicitou isso, ignore este e-mail.
"""

        enviar_email(email, assunto, mensagem)
        return True

    except Exception as e:
        logger.error(f"Erro ao solicitar reset de senha: {e}")
        return False


# -------------------------------------------------
# 2) Validar token de reset
# -------------------------------------------------

def validar_token_reset(token):
    try:
        if not validar_token_simples(token):
            return False, None

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT usuario_id FROM reset_senhas WHERE token = ?", (token,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return False, None

        return True, row[0]

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return False, None


# -------------------------------------------------
# 3) Redefinir senha e remover token
# -------------------------------------------------

def redefinir_senha(usuario_id, nova_senha, token):
    try:
        senha_hash = gerar_hash_senha(nova_senha)

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuarios
            SET senha = ?
            WHERE id = ?
        """, (senha_hash, usuario_id))

        cursor.execute("""
            DELETE FROM reset_senhas
            WHERE token = ?
        """, (token,))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}")
        return False

