# PETdor_2_0/utils/email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

# Configurações de e-mail (idealmente de variáveis de ambiente)
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587)) # Default para TLS
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "relatorio@petdor.app") # Usando o e-mail central

def _enviar_email_generico(destinatario: str, assunto: str, corpo_html: str):
    """Função interna para enviar e-mails."""
    if not all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]):
        logger.error("Configurações de e-mail incompletas. Não é possível enviar e-mail.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_SENDER
    msg["To"] = destinatario

    # Adiciona a versão HTML do corpo
    msg.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls() # Inicia a criptografia TLS
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, destinatario, msg.as_string())
        logger.info(f"E-mail enviado com sucesso para {destinatario} (Assunto: {assunto})")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Falha de autenticação SMTP ao enviar e-mail para {destinatario}: {e}")
        # Lembrete da memória: "continua enfrentando falha de autenticação SMTP (erro 535 Authentication unsuccessful)"
        # Isso indica que as credenciais EMAIL_USER/EMAIL_PASSWORD podem estar incorretas ou o app não tem permissão.
        # Verifique as variáveis de ambiente no Streamlit Cloud e as configurações do seu provedor (GoDaddy).
        return False
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {destinatario}: {e}", exc_info=True)
        return False

def enviar_email_confirmacao(destinatario: str, nome_usuario: str, token: str):
    """Envia um e-mail de confirmação de conta."""
    assunto = "Confirme sua conta PETDor"
    # URL de confirmação (ajuste para o seu domínio real no Streamlit Cloud)
    # Exemplo: https://petdor.streamlit.app/confirmar_email?token={token}
    # Ou se você já tem o domínio petdor.app redirecionado: https://petdor.app/confirmar_email?token={token}
    confirm_url = f"https://petdor.streamlit.app/confirmar_email?token={token}" 

    corpo_html = f"""
    <html>
        <body>
            <p>Olá, {nome_usuario},</p>
            <p>Obrigado por se cadastrar no PETDor! Por favor, clique no link abaixo para confirmar seu e-mail:</p>
            <p><a href="{confirm_url}">Confirmar E-mail</a></p>
            <p>Se você não solicitou este cadastro, por favor, ignore este e-mail.</p>
            <p>Atenciosamente,</p>
            <p>Equipe PETDor</p>
        </body>
    </html>
    """
    return _enviar_email_generico(destinatario, assunto, corpo_html)

# --- NOVA FUNÇÃO PARA RESET DE SENHA ---
def enviar_email_reset_senha(destinatario: str, nome_usuario: str, token: str):
    """Envia um e-mail com o link para redefinir a senha."""
    assunto = "Redefinição de Senha PETDor"
    # URL de reset de senha (ajuste para o seu domínio real no Streamlit Cloud)
    # Exemplo: https://petdor.streamlit.app/redefinir_senha?token={token}
    # Ou se você já tem o domínio petdor.app redirecionado: https://petdor.app/redefinir_senha?token={token}
    reset_url = f"https://petdor.streamlit.app/redefinir_senha?token={token}"

    corpo_html = f"""
    <html>
        <body>
            <p>Olá, {nome_usuario},</p>
            <p>Recebemos uma solicitação para redefinir a senha da sua conta PETDor.</p>
            <p>Por favor, clique no link abaixo para criar uma nova senha:</p>
            <p><a href="{reset_url}">Redefinir Senha</a></p>
            <p>Este link é válido por 1 hora. Se você não solicitou a redefinição de senha, por favor, ignore este e-mail.</p>
            <p>Atenciosamente,</p>
            <p>Equipe PETDor</p>
        </body>
    </html>
    """
    return _enviar_email_generico(destinatario, assunto, corpo_html)

# Você pode adicionar outras funções de envio de e-mail aqui, se necessário.
