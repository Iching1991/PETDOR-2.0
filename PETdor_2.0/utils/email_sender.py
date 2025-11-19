# PETdor_2.0/utils/email_sender.py

"""
Envio de e-mails do PETDor:
- confirmação de cadastro
- recuperação de senha
As credenciais SMTP vêm de variáveis de ambiente (.env).
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from dotenv import load_dotenv # <-- CORREÇÃO: Removido o texto extra aqui!

logger = logging.getLogger(__name__)

# Carrega variáveis do .env na raiz do projeto
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")      # ex: no-reply@petdor.app
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USERNAME or "no-reply@petdor.app")

def _enviar_email(
    destinatario: str,
    assunto: str,
    corpo_html: str,
    corpo_texto: Optional[str] = None,
) -> bool:
    """
    Função interna genérica para enviar e-mail via SMTP.
    """
    if not (SMTP_USERNAME and SMTP_PASSWORD):
        logger.error(
            "Credenciais SMTP não configuradas (SMTP_USERNAME / SMTP_PASSWORD)."
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_EMAIL
    msg["To"] = destinatario
    msg["Subject"] = assunto

    if corpo_texto is None:
        import re
        corpo_texto = re.sub("<[^<]+?>", "", corpo_html)

    msg.attach(MIMEText(corpo_texto, "plain", "utf-8"))
    msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        logger.info(
            "E-mail enviado para %s com assunto '%s'", destinatario, assunto
        )
        return True
    except Exception as e:
        logger.error(
            "Falha ao enviar e-mail para %s: %s", destinatario, e, exc_info=True
        )
        return False

# -------------------------------------------------
# Confirmação de e-mail de cadastro
# -------------------------------------------------
def enviar_email_confirmacao(
    destinatario: str,
    nome_usuario: str,
    token: str,
) -> bool:
    """
    Envia e-mail de confirmação de cadastro.
    Usado por auth.user.cadastrar_usuario.
    """
    assunto = "Confirme seu cadastro no PETDor"
    link = f"http://localhost:8501/?pagina=confirmar_email&token={token}"
    corpo_html = f"""
    <html>
      <body>
        <p>Olá, {nome_usuario},</p>
        <p>Obrigado por se cadastrar no PETDor!</p>
        <p>Para ativar sua conta, clique no link abaixo:</p>
        <p><a href="{link}">Confirmar meu e-mail</a></p>
        <p>Se você não fez este cadastro, pode ignorar esta mensagem.</p>
        <p>Abraços,<br>Equipe PETDor</p>
      </body>
    </html>
    """
    corpo_texto = f"""
Olá, {nome_usuario},
Obrigado por se cadastrar no PETDor!
Para ativar sua conta, acesse o link abaixo:
{link}
Se você não fez este cadastro, pode ignorar esta mensagem.
Abraços,
Equipe PETDor
""".strip()
    return _enviar_email(destinatario, assunto, corpo_html, corpo_texto)

# -------------------------------------------------
# Recuperação de senha
# -------------------------------------------------
def enviar_email_recuperacao_senha(
    destinatario: str,
    nome_usuario: str,
    token: str,
) -> bool:
    """
    Envia e-mail com link de recuperação de senha.
    Usado por auth.password_reset.reset_password_request.
    """
    assunto = "Recuperação de senha - PETDor"
    link = f"http://localhost:8501/?pagina=reset_senha&token={token}"
    corpo_html = f"""
    <html>
      <body>
        <p>Olá, {nome_usuario},</p>
        <p>Recebemos uma solicitação para redefinir a senha da sua conta PETDor.</p>
        <p>Para redefinir sua senha, clique no link abaixo:</p>
        <p><a href="{link}">Redefinir minha senha</a></p>
        <p>Se você não fez esta solicitação, pode ignorar este e-mail.</p>
        <p>Abraços,<br>Equipe PETDor</p>
      </body>
    </html>
    """
    corpo_texto = f"""
Olá, {nome_usuario},
Recebemos uma solicitação para redefinir a senha da sua conta PETDor.
Para redefinir sua senha, acesse o link abaixo:
{link}
Se você não fez esta solicitação, pode ignorar esta mensagem.
Abraços,
Equipe PETDor
""".strip()
    return _enviar_email(destinatario, assunto, corpo_html, corpo_texto)
