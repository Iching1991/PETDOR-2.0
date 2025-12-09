# PetDor2/backend/utils/email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Tuple

from backend.utils.config import (
    SMTP_SERVIDOR,
    SMTP_PORTA,
    SMTP_EMAIL,
    SMTP_SENHA,
    SMTP_USAR_SSL,
)

logger = logging.getLogger(__name__)


def _criar_mensagem(
    destinatario: str, assunto: str, corpo_texto: str, corpo_html: str
) -> MIMEMultipart:
    """Cria objeto MIME corretamente configurado."""
    mensagem = MIMEMultipart("alternative")
    mensagem["From"] = SMTP_EMAIL
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto

    mensagem.attach(MIMEText(corpo_texto, "plain"))
    mensagem.attach(MIMEText(corpo_html, "html"))

    return mensagem


def _enviar_mensagem(destinatario: str, mensagem: MIMEMultipart) -> Tuple[bool, str]:
    """Responsável apenas por abrir conexão SMTP e enviar a mensagem."""
    try:
        if SMTP_USAR_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVIDOR, SMTP_PORTA)
        else:
            server = smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA)
            server.starttls()

        server.login(SMTP_EMAIL, SMTP_SENHA)
        server.sendmail(SMTP_EMAIL, destinatario, mensagem.as_string())
        server.quit()

        logger.info(f"📨 E-mail enviado com sucesso para {destinatario}")
        return True, "E-mail enviado com sucesso."

    except Exception as erro:
        logger.error(
            f"❌ Falha ao enviar e-mail para {destinatario}: {erro}",
            exc_info=True
        )
        return False, f"Erro ao enviar e-mail: {erro}"


def enviar_email_confirmacao_generico(
    destinatario_email: str,
    assunto: str,
    corpo_html: str,
    corpo_texto: str
) -> Tuple[bool, str]:
    """Função única e genérica para envio de e-mails."""
    msg = _criar_mensagem(destinatario_email, assunto, corpo_texto, corpo_html)
    return _enviar_mensagem(destinatario_email, msg)
