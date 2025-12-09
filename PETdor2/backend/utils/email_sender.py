# backend/utils/email_sender.py

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple

from backend.utils.config import (
    SMTP_SERVIDOR,
    SMTP_PORTA,
    SMTP_EMAIL,
    SMTP_SENHA,
    SMTP_USAR_SSL,
)

logger = logging.getLogger(__name__)


def _criar_mensagem(destinatario: str, assunto: str, corpo_texto: str, corpo_html: str) -> MIMEMultipart:
    """Cria a estrutura do email com partes texto e HTML."""
    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_EMAIL
    msg["To"] = destinatario
    msg["Subject"] = assunto

    msg.attach(MIMEText(corpo_texto, "plain"))
    msg.attach(MIMEText(corpo_html, "html"))

    return msg


def _enviar_email(destinatario: str, mensagem: MIMEMultipart) -> Tuple[bool, str]:
    """Envia efetivamente o e-mail via SMTP."""
    try:
        if SMTP_USAR_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVIDOR, SMTP_PORTA)
        else:
            server = smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA)
            server.starttls()

        server.login(SMTP_EMAIL, SMTP_SENHA)
        server.sendmail(SMTP_EMAIL, destinatario, mensagem.as_string())
        server.quit()

        logger.info(f"📨 Email enviado para {destinatario}")
        return True, "E-mail enviado com sucesso."

    except Exception as e:
        logger.error(f"❌ Erro ao enviar e-mail para {destinatario}: {e}", exc_info=True)
        return False, f"Erro ao enviar e-mail: {e}"


# ---------------------------------------------------------------------------
# ✔ FUNÇÃO GENÉRICA (base para todas)
# ---------------------------------------------------------------------------

def enviar_email_generico(
    destinatario_email: str,
    assunto: str,
    corpo_html: str,
    corpo_texto: str,
) -> Tuple[bool, str]:
    """Função central utilizada por todas as outras."""
    msg = _criar_mensagem(destinatario_email, assunto, corpo_texto, corpo_html)
    return _enviar_email(destinatario_email, msg)


# ---------------------------------------------------------------------------
# ✔ FUNÇÕES ESPECÍFICAS (mantidas para compatibilidade)
# ---------------------------------------------------------------------------

def enviar_email_confirmacao_conta(destinatario: str, link: str) -> Tuple[bool, str]:
    """Usada em auth/email_confirmation.py"""
    assunto = "Confirme sua conta - PetDor"
    corpo_texto = f"Olá! Confirme sua conta acessando: {link}"
    corpo_html = f"""
        <p>Olá!</p>
        <p>Confirme sua conta clicando no link abaixo:</p>
        <a href="{link}">Confirmar conta</a>
    """

    return enviar_email_generico(destinatario, assunto, corpo_html, corpo_texto)


def enviar_email_recuperacao_senha(destinatario: str, link: str) -> Tuple[bool, str]:
    """Usada em auth/password_reset.py — necessária para evitar seu erro atual."""
    assunto = "Recuperação de senha - PetDor"
    corpo_texto = f"Para redefinir sua senha, acesse: {link}"
    corpo_html = f"""
        <p>Você solicitou a recuperação de senha.</p>
        <p>Clique no link abaixo para redefinir:</p>
        <a href="{link}">Redefinir senha</a>
    """

    return enviar_email_generico(destinatario, assunto, corpo_html, corpo_texto)
