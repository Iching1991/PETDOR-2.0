# PetDor2/backend/utils/email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from typing import Tuple

logger = logging.getLogger(__name__)

# Importa variáveis SMTP do config
# Certifique-se de que backend/utils/config.py existe e define estas variáveis
from backend.utils.config import (
    SMTP_SERVIDOR,
    SMTP_PORTA,
    SMTP_EMAIL,
    SMTP_SENHA,
    SMTP_USAR_SSL,
)

def enviar_email_confirmacao_generico(
    destinatario_email: str,
    assunto: str,
    corpo_html: str,
    corpo_texto: str
) -> Tuple[bool, str]:
    """
    Função genérica para enviar e-mails com corpo HTML e texto.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_EMAIL
        msg["To"] = destinatario_email
        msg["Subject"] = assunto

        # Anexa as partes de texto e HTML
        msg.attach(MIMEText(corpo_texto, "plain"))
        msg.attach(MIMEText(corpo_html, "html"))

        with smtplib.SMTP_SSL(SMTP_SERVIDOR, SMTP_PORTA) if SMTP_USAR_SSL else smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA) as server:
            if not SMTP_USAR_SSL:
                server.starttls() # Inicia TLS se não for SMTP_SSL
            server.login(SMTP_EMAIL, SMTP_SENHA)
            server.sendmail(SMTP_EMAIL, destinatario_email, msg.as_string())

        logger.info(f"✅ E-mail enviado com sucesso para {destinatario_email} - Assunto: {assunto}")
        return True, "E-mail enviado com sucesso."

    except Exception as e:
        logger.error(f"❌ Falha ao enviar e-mail para {destinatario_email} - Assunto: {assunto}: {e}", exc_info=True)
        return False, f"Erro ao enviar e-mail: {e}"

# Funções específicas de confirmação e reset de senha foram movidas para auth/email_confirmation.py e auth/password_reset.py
# ou são chamadas a partir de lá usando a função genérica acima.
