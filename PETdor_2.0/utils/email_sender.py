# PETdor_2_0/utils/email_sender.py
"""
Módulo para envio de e-mails do sistema PETDOR.
Suporta confirmação de conta e reset de senha.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

# Configurações de e-mail (de variáveis de ambiente)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.godaddy.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "relatorio@petdor.app")

def _enviar_email_generico(destinatario: str, assunto: str, corpo_html: str) -> bool:
    """
    Função interna para enviar e-mails usando SMTP.
    Retorna True se enviado com sucesso, False caso contrário.
    """
    # Verifica se as configurações estão completas
    if not all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]):
        logger.error("Configurações de e-mail incompletas. Verifique EMAIL_USER, EMAIL_PASSWORD e EMAIL_HOST.")
        return False

    # Cria a mensagem
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_SENDER
    msg["To"] = destinatario

    # Adiciona o corpo HTML
    msg.attach(MIMEText(corpo_html, "html"))

    try:
        # Conecta ao servidor SMTP
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()  # Inicia TLS
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, destinatario, msg.as_string())

        logger.info(f"E-mail enviado com sucesso para {destinatario} (Assunto: {assunto})")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Falha de autenticação SMTP para {destinatario}: {e}")
        logger.error("Verifique EMAIL_USER e EMAIL_PASSWORD nas variáveis de ambiente")
        return False

    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Destinatário recusado para {destinatario}: {e}")
        return False

    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {destinatario}: {e}", exc_info=True)
        return False

def enviar_email_confirmacao(destinatario: str, nome_usuario: str, token: str) -> bool:
    """
    Envia e-mail de confirmação de conta para novo usuário.

    Args:
        destinatario: E-mail do usuário
        nome_usuario: Nome do usuário
        token: Token de confirmação

    Returns:
        bool: True se enviado com sucesso
    """
    assunto = "🎾 Confirme sua conta no PETDOR"

    # URL de confirmação (ajuste para seu domínio)
    confirm_url = f"https://petdor.streamlit.app/confirmar_email?token={token}"

    corpo_html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .button {{ background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐾 Bem-vindo ao PETDOR!</h1>
                </div>
                <p>Olá, <strong>{nome_usuario}</strong>,</p>
                <p>Obrigado por se cadastrar no <strong>PETDOR</strong> - seu sistema de avaliação de dor animal!</p>
                <p>Para completar seu cadastro, clique no botão abaixo para confirmar seu e-mail:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{confirm_url}" class="button">Confirmar E-mail</a>
                </p>
                <p><em>Ou copie e cole este link no seu navegador:</em><br>
                <a href="{confirm_url}">{confirm_url}</a></p>
                <p>Se você não solicitou este cadastro, por favor, ignore este e-mail.</p>
                <hr>
                <div class="footer">
                    <p>Atenciosamente,<br>
                    <strong>Equipe PETDOR</strong><br>
                    <a href="https://petdor.streamlit.app">petdor.streamlit.app</a></p>
                </div>
            </div>
        </body>
    </html>
    """

    return _enviar_email_generico(destinatario, assunto, corpo_html)

def enviar_email_reset_senha(destinatario: str, nome_usuario: str, token: str) -> bool:
    """
    Envia e-mail com link para redefinir senha.

    Args:
        destinatario: E-mail do usuário
        nome_usuario: Nome do usuário
        token: Token de reset de senha

    Returns:
        bool: True se enviado com sucesso
    """
    assunto = "🔑 Redefinição de Senha - PETDOR"

    # URL de reset de senha (ajuste para seu domínio)
    reset_url = f"https://petdor.streamlit.app/redefinir_senha?token={token}"

    corpo_html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ff9800; color: white; padding: 20px; text-align: center; }}
                .button {{ background-color: #ff9800; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔑 Redefinir Senha PETDOR</h1>
                </div>
                <p>Olá, <strong>{nome_usuario}</strong>,</p>
                <p>Recebemos uma solicitação para redefinir a senha da sua conta no <strong>PETDOR</strong>.</p>
                <p>Se você solicitou esta redefinição, clique no botão abaixo para criar uma nova senha:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" class="button">Redefinir Senha</a>
                </p>
                <p><em>Ou copie e cole este link no seu navegador:</em><br>
                <a href="{reset_url}">{reset_url}</a></p>

                <div class="warning">
                    <strong>⚠️ Importante:</strong> Este link é válido por apenas <strong>1 hora</strong>. 
                    Se você não solicitou a redefinição de senha, por favor, ignore este e-mail.
                </div>

                <hr>
                <div class="footer">
                    <p>Atenciosamente,<br>
                    <strong>Equipe PETDOR</strong><br>
                    <a href="https://petdor.streamlit.app">petdor.streamlit.app</a></p>
                </div>
            </div>
        </body>
    </html>
    """

    return _enviar_email_generico(destinatario, assunto, corpo_html)

# Função adicional para testes (opcional)
def testar_configuracao_email() -> dict:
    """
    Testa se a configuração de e-mail está funcionando.
    Útil para debug.

    Returns:
        dict: Status das configurações e teste de conexão
    """
    status = {
        "configuracoes_completas": all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]),
        "email_host": EMAIL_HOST,
        "email_port": EMAIL_PORT,
        "email_sender": EMAIL_SENDER,
        "conexao_smtp": False
    }

    if status["configuracoes_completas"]:
        try:
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                status["conexao_smtp"] = True
        except Exception as e:
            status["erro_smtp"] = str(e)

    return status
