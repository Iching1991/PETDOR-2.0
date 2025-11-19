# PETdor_2.0/auth/password_reset.py

"""
Módulo para gerenciamento de recuperação e redefinição de senha.
"""
import uuid
from datetime import datetime, timedelta
import logging
import bcrypt
from database.connection import conectar_db
from database.models import buscar_usuario_por_email
from utils.email_sender import enviar_email_recuperacao_senha # <-- Esta linha deve estar EXATAMENTE assim

logger = logging.getLogger(__name__)

# -------------------------
# Solicitar recuperação de senha (usada por pages.recuperar_senha)
# -------------------------
def reset_password_request(email: str) -> tuple[bool, str]:
    """
    Gera um token de recuperação de senha e envia por e-mail.
    """
    try:
        usuario = buscar_usuario_por_email(email)
        if not usuario:
            # Para segurança, não informamos se o e-mail existe ou não
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."<pre><code>    token = str(uuid.uuid4())
    expiracao = datetime.now() + timedelta(hours=1) # Token válido por 1 hora<pre><code>conn = conectar_db()
cursor = conn.cursor()

# Inserir o token na tabela password_resets
cursor.execute("""
    INSERT INTO password_resets (usuario_id, token, criado_em, utilizado)
    VALUES (?, ?, ?, 0)
""", (usuario.id, token, expiracao.strftime("%Y-%m-%d %H:%M:%S"))) # &amp;lt;-- usuario.id (acesso por ponto)
conn.commit()
conn.close()

# Envia o e-mail com o link de recuperação
sucesso_email = enviar_email_recuperacao_senha(email, usuario.nome, token) # &amp;lt;-- usuario.nome (acesso por ponto)
if not sucesso_email:
    logger.warning(f"Falha ao enviar e-mail de recuperação para {email}.")
    return False, "Erro ao enviar e-mail de recuperação. Tente novamente mais tarde."

return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."
