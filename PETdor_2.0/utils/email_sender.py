# PETdor_2_0/utils/email_sender.py
"""
Módulo de envio de e-mails do PETDOR.
Suporta confirmação de conta e redefinição de senha.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# CONFIGURAÇÕES DE E-MAIL
# -----------------------------

# GoDaddy SMTP correto (caso o usuário não defina por variável de ambiente)
DEFAULT_GODADDY_SMTP = "smtpout.secureserver.net"

EMAIL_HOST = os.getenv("EMAIL_HOST", DEFAULT_GODADDY_SMTP)
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))  # TLS padrão
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "relatorio@petdor.app")

# -----------------------------
# Função interna genérica
# -----------------------------
def _enviar_email_generico(destinatario: str, assunto: str, corpo_html: str) -> bool:
    """
    Envia um e-mail HTML via SMTP.
    Retorna True se enviado com sucesso.
    """

    # Verificação básica de configuração
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.error("❌ EMAIL_USER ou EMAIL_PASSWORD não configurados.")
        return False

    if not EMAIL_HOST:
        logger.error("❌ EMAIL_HOST não configurado.")
        return False

    if not EMAIL_SENDER:
        logger.error("❌ EMAIL_SENDER vazio. Configure EMAIL_SENDER nas variáveis.")
        return False

    # Monta mensagem
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_SENDER
    msg["To"] = destinatario

    # Corpo HTML
    msg.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()             # Godaddy exige STARTTLS
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, destinatario, msg.as_string())

        logger.info(f"📧 E-mail enviado para {destinatario} - Assunto: {assunto}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Falha de autenticação SMTP: {e}")
        return False

    except smtplib.SMTPConnectError as e:
        logger.error(f"❌ Erro de conexão SMTP: {e}")
        return False

    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"❌ Destinatário recusado: {destinatario} | Erro: {e}")
        return False

    except Exception as e:
        logger.error(f"❌ Erro geral ao enviar e-mail: {e}", exc_info=True)
        return False


# -----------------------------
# CONFIRMAÇÃO DE CONTA
# -----------------------------
def enviar_email_confirmacao(destinatario: str, nome_usuario: str, token: str) -> bool:
    """
    Envia e-mail de confirmação de conta.
    """
    assunto = "🎾 Confirme sua conta no PETDOR"
    confirm_url = f"https://petdor.streamlit.app/confirmar_email?token={token}"

    corpo_html = f"""
    <html>
        <body style="font-family: Arial; color:#333;">
            <h2 style="background:#4CAF50; color:white; padding:15px; text-align:center;">
                Confirmação de Conta PETDOR
            </h2>

            <p>Olá, <strong>{nome_usuario}</strong>,</p>
            <p>Obrigado por se cadastrar no <strong>PETDOR</strong>! Clique abaixo para confirmar seu e-mail:</p>

            <p style="text-align:center;">
                <a href="{confirm_url}" 
                   style="background:#4CAF50; color:white; padding:12px 25px; border-radius:6px; text-decoration:none;">
                   Confirmar E-mail
                </a>
            </p>

            <p>Ou copie o link:<br>{confirm_url}</p>

            <hr>
            <p style="text-align:center; color:#666; font-size:12px;">
                Equipe PETDOR — <a href="https://petdor.streamlit.app">petdor.streamlit.app</a>
            </p>
        </body>
    </html>
    """

    return _enviar_email_generico(destinatario, assunto, corpo_html)


# -----------------------------
# RESET DE SENHA
# -----------------------------
def enviar_email_reset_senha(destinatario: str, nome_usuario: str, token: str) -> bool:
    """
    Envia e-mail para redefinição de senha.
    """
    assunto = "🔑 Redefinição de Senha - PETDOR"
    reset_url = f"https://petdor.streamlit.app/redefinir_senha?token={token}"

    corpo_html = f"""
    <html>
        <body style="font-family: Arial; color:#333;">
            <h2 style="background:#ff9800; color:white; padding:15px; text-align:center;">
                Redefinir Senha PETDOR
            </h2>

            <p>Olá, <strong>{nome_usuario}</strong>,</p>
            <p>Você solicitou redefinir sua senha. Clique abaixo:</p>

            <p style="text-align:center;">
                <a href="{reset_url}"
                   style="background:#ff9800; color:white; padding:12px 25px; border-radius:6px; text-decoration:none;">
                   Redefinir Senha
                </a>
            </p>

            <p>Ou copie o link:<br>{reset_url}</p>

            <p style="background:#fff3cd; border:1px solid #ffeaa7; padding:10px; border-radius:5px;">
                ⚠️ Este link expira em <strong>1 hora</strong>.
            </p>

            <hr>
            <p style="text-align:center; color:#666; font-size:12px;">
                Equipe PETDOR — <a href="https://petdor.streamlit.app">petdor.streamlit.app</a>
            </p>
        </body>
    </html>
    """

    return _enviar_email_generico(destinatario, assunto, corpo_html)


# -----------------------------
# TESTE DE CONFIGURAÇÃO SMTP
# -----------------------------
def testar_configuracao_email() -> dict:
    """
    Testa a conexão com o servidor de e-mail.
    Útil para debug via Streamlit.
    """
    status = {
        "EMAIL_HOST": EMAIL_HOST,
        "EMAIL_PORT": EMAIL_PORT,
        "EMAIL_USER": EMAIL_USER,
        "EMAIL_SENDER": EMAIL_SENDER,
        "configuracoes_ok": all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]),
        "conexao_smtp": False
    }

    if status["configuracoes_ok"]:
        try:
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                status["conexao_smtp"] = True
        except Exception as e:
            status["erro_smtp"] = str(e)

    return status
