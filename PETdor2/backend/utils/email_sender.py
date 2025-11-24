# PETdor2/utils/email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import ssl

logger = logging.getLogger(__name__)

def enviar_email(destinatario, assunto, corpo_html):
    """Função genérica para enviar e-mails."""
    smtp_server = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT", 587))
    smtp_user = os.getenv("EMAIL_USER")
    smtp_password = os.getenv("EMAIL_PASSWORD")
    sender_email = os.getenv("EMAIL_SENDER")

    if not all([smtp_server, smtp_user, smtp_password, sender_email]):
        logger.error("Variáveis de ambiente de e-mail não configuradas. Não é possível enviar e-mail.")
        return False, "Configuração de e-mail ausente."

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = destinatario
    msg["Subject"] = assunto

    msg.attach(MIMEText(corpo_html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, destinatario, msg.as_string())
        logger.info(f"E-mail enviado com sucesso para {destinatario} (Assunto: {assunto}).")
        return True, "E-mail enviado com sucesso."
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Erro de autenticação SMTP ao enviar e-mail para {destinatario}: {e}", exc_info=True)
        return False, f"Erro de autenticação SMTP. Verifique as credenciais do e-mail: {e}"
    except smtplib.SMTPConnectError as e:
        logger.error(f"Erro de conexão SMTP ao enviar e-mail para {destinatario}: {e}", exc_info=True)
        return False, f"Erro de conexão SMTP. Verifique o servidor e a porta: {e}"
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar e-mail para {destinatario}: {e}", exc_info=True)
        return False, f"Erro inesperado ao enviar e-mail: {e}"

def enviar_email_confirmacao(destinatario_email, nome_usuario, link_confirmacao):
    """Envia um e-mail de confirmação de conta."""
    assunto = "Confirme seu e-mail para o PETDOR"
    corpo_html = f"""
    <html>
        <body>
            <p>Olá, {nome_usuario}!</p>
            <p>Obrigado por se cadastrar no PETDOR.</p>
            <p>Por favor, clique no link abaixo para confirmar seu e-mail:</p>
            <p><a href="{link_confirmacao}">Confirmar E-mail</a></p>
            <p>Se você não solicitou este cadastro, por favor, ignore este e-mail.</p>
            <p>Atenciosamente,</p>
            <p>Equipe PETDOR</p>
        </body>
    </html>
    """
    return enviar_email(destinatario_email, assunto, corpo_html)

def enviar_email_recuperacao_senha(destinatario_email, nome_usuario, link_reset):
    """Envia um e-mail com o link para redefinição de senha."""
    assunto = "Redefinição de Senha PETDOR"
    corpo_html = f"""
    <html>
        <body>
            <p>Olá, {nome_usuario}!</p>
            <p>Você solicitou a redefinição da sua senha no PETDOR.</p>
            <p>Por favor, clique no link abaixo para criar uma nova senha:</p>
            <p><a href="{link_reset}">Redefinir Senha</a></p>
            <p>Este link é válido por 1 hora.</p>
            <p>Se você não solicitou a redefinição de senha, por favor, ignore este e-mail.</p>
            <p>Atenciosamente,</p>
            <p>Equipe PETDOR</p>
        </body>
    </html>
    """
    return enviar_email(destinatario_email, assunto, corpo_html)
