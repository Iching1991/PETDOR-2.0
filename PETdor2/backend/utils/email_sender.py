# backend/utils/email_sender.py

import smtplib
import logging
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


# ============================================================
#   CARREGAR CONFIGURAÇÕES AUTOMATICAMENTE
# ============================================================

def _load_smtp_config():
    """Carrega automaticamente SMTP de st.secrets ou variáveis de ambiente."""
    try:
        email_cfg = st.secrets["email"]

        return {
            "host": email_cfg.get("EMAIL_HOST"),
            "port": email_cfg.get("EMAIL_PORT"),
            "user": email_cfg.get("EMAIL_USER"),
            "password": email_cfg.get("EMAIL_PASSWORD"),
            "sender": email_cfg.get("EMAIL_SENDER"),
        }

    except Exception as e:
        logger.error("❌ Erro carregando SMTP do st.secrets", exc_info=True)
        raise RuntimeError("Falha ao carregar configurações SMTP.") from e


SMTP = _load_smtp_config()


# ============================================================
#   FUNÇÃO INTERNA — ENVIO DE EMAIL
# ============================================================

def _enviar_email(
    destinatario: str,
    assunto: str,
    corpo_texto: str,
    corpo_html: str
) -> Tuple[bool, str]:
    """
    Envia e-mail com corpo texto + HTML.
    """

    if not destinatario:
        return False, "Endereço de e-mail vazio."

    try:
        # Montagem da mensagem
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP["sender"]
        msg["To"] = destinatario
        msg["Subject"] = assunto

        msg.attach(MIMEText(corpo_texto, "plain"))
        msg.attach(MIMEText(corpo_html, "html"))

        # Conexão SMTP
        server = smtplib.SMTP(SMTP["host"], SMTP["port"])
        server.starttls()

        server.login(SMTP["user"], SMTP["password"])
        server.sendmail(SMTP["sender"], destinatario, msg.as_string())
        server.quit()

        logger.info(f"📧 Email enviado → {destinatario} | Assunto: {assunto}")

        return True, "E-mail enviado com sucesso."

    except Exception as e:
        logger.error(f"❌ Falha ao enviar e-mail → {destinatario}: {e}", exc_info=True)
        return False, f"Erro ao enviar e-mail: {e}"


# ============================================================
#   FUNÇÕES PÚBLICAS
# ============================================================

def enviar_email_confirmacao_generico(
    destinatario_email: str,
    assunto: str,
    corpo_html: str,
    corpo_texto: str
) -> Tuple[bool, str]:
    """Envia e-mail de confirmação genérico."""
    return _enviar_email(destinatario_email, assunto, corpo_texto, corpo_html)


def enviar_email_recuperacao_senha(
    destinatario_email: str,
    link_recuperacao: str
) -> Tuple[bool, str]:
    """Envia e-mail com link de recuperação de senha."""

    assunto = "Recuperação de Senha - PetDor"

    corpo_texto = (
        "Olá! Você solicitou a recuperação da sua senha.\n\n"
        f" Clique no link:\n{link_recuperacao}\n\n"
        "Se não foi você, ignore este e-mail."
    )

    corpo_html = f"""
    <p>Olá! Você solicitou a recuperação da sua senha.</p>
    <p>Clique no botão abaixo:</p>

    <a href="{link_recuperacao}"
       style="padding:12px 22px; background:#4CAF50; color:white;
              text-decoration:none; border-radius:6px; font-weight:bold;">
        Redefinir Senha
    </a>

    <p>Se não foi você, basta ignorar este e-mail.</p>
    """

    return _enviar_email(destinatario_email, assunto, corpo_texto, corpo_html)


__all__ = [
    "enviar_email_confirmacao_generico",
    "enviar_email_recuperacao_senha",
]
