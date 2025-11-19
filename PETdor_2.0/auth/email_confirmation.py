# PETdor_2.0/auth/email_confirmation.py

import logging
from database.connection import conectar_db
from utils.tokens import validar_token_simples
from utils.email_sender import enviar_email_confirmacao # <--- ESTA LINHA FOI CORRIGIDA!

logger = logging.getLogger(__name__)

def confirmar_email(token: str) -> bool:
    """
    Confirma o e-mail de um usuário usando um token.
    """
    try:
        if not validar_token_simples(token):
            logger.warning(f"Tentativa de confirmação de e-mail com token inválido: {token}")
            return False

        conn = conectar_db()
        cursor = conn.cursor()

        # Busca o usuário associado ao token de confirmação
        cursor.execute("SELECT id FROM usuarios WHERE email_confirm_token = ? AND email_confirmado = 0", (token,))
        usuario_id_row = cursor.fetchone()

        if not usuario_id_row:
            conn.close()
            logger.warning(f"Token de confirmação de e-mail não encontrado ou já utilizado: {token}")
            return False

        usuario_id = usuario_id_row[0]

        # Atualiza o status de confirmação do e-mail e limpa o token
        cursor.execute("""
            UPDATE usuarios
            SET email_confirmado = 1, email_confirm_token = NULL
            WHERE id = ?
        """, (usuario_id,))
        conn.commit()
        conn.close()

        logger.info(f"E-mail do usuário {usuario_id} confirmado com sucesso.")
        return True

    except Exception as e:
        logger.error(f"Erro ao confirmar e-mail com token {token}: {e}", exc_info=True)
        return False

# Esta função pode ser usada para reenviar o e-mail de confirmação, se necessário
def reenviar_email_confirmacao(email: str) -> bool:
    """
    Gera um novo token de confirmação e reenvia o e-mail.
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email_confirm_token FROM usuarios WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return False # Não revela se o e-mail existe por segurança

        usuario_id, nome, token_existente = row

        # Se já existe um token e o e-mail não foi confirmado, podemos reutilizá-lo ou gerar um novo
        # Por simplicidade, vamos assumir que o token é gerado no cadastro e apenas reenviado aqui.
        # Se você quiser gerar um novo token aqui, precisaria importar 'gerar_token_simples' e atualizar o banco.

        if not token_existente:
            # Se não há token, o usuário não passou pelo cadastro completo ou o token foi limpo.
            # Seria necessário gerar um novo token e atualizar o banco aqui.
            # Por enquanto, vamos retornar False para indicar que o processo não pode ser concluído.
            logger.warning(f"Tentativa de reenviar e-mail de confirmação para {email}, mas nenhum token existente.")
            return False

        # Envia o e-mail usando a função correta
        ok_envio = enviar_email_confirmacao(email, nome, token_existente)
        if ok_envio:
            logger.info(f"E-mail de confirmação reenviado para {email}.")
            return True
        else:
            logger.error(f"Falha ao reenviar e-mail de confirmação para {email}.")
            return False

    except Exception as e:
        logger.error(f"Erro ao reenviar e-mail de confirmação para {email}: {e}", exc_info=True)
        return False

