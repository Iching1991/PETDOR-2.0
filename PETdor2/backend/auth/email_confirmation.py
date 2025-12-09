# PetDor2/backend/auth/email_confirmation.py
"""
Módulo de confirmação de e-mail do PETDor.
Gerencia geração e validação de tokens de confirmação.
"""

import logging
from datetime import datetime
from typing import Tuple, Dict, Any

# Importações absolutas — evita loops de import
from backend.database.supabase_client import (
    supabase_table_update,
    supabase_table_select
)

from backend.auth.security import (
    gerar_token_confirmacao_email,
    validar_token_confirmacao_email
)

from backend.auth.user import (
    marcar_email_como_confirmado,
    buscar_usuario_por_email
)

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"


# =====================================================================
# 1. GERAR E ENVIAR E-MAIL DE CONFIRMAÇÃO
# =====================================================================
def enviar_email_confirmacao(email: str, nome: str, user_id: int) -> Tuple[bool, str]:
    """
    Gera token JWT, salva no banco e envia o link de confirmação para o usuário.
    """

    # Import tardio — evita ciclos com utils
    from backend.utils.email_sender import enviar_email_confirmacao_generico
    from backend.utils.config import STREAMLIT_APP_URL

    try:
        # 1 — Gerar token
        token = gerar_token_confirmacao_email(email, user_id)

        # 2 — Salvar token no banco
        dados_update = {
            "email_confirm_token": token,
            "atualizado_em": datetime.utcnow().isoformat()
        }

        ok_update, msg_update = supabase_table_update(
            TABELA_USUARIOS,
            dados_update,
            {"id": user_id}
        )

        if not ok_update:
            logger.error(f"[CONF-EMAIL] Falha ao salvar token: {msg_update}")
            return False, "Erro ao gerar link de confirmação."

        # 3 — Monta URL para confirmação
        link = f"{STREAMLIT_APP_URL}?action=confirm_email&token={token}"

        # 4 — Conteúdo do e-mail
        assunto = "Confirme seu e-mail - PETDor"

        corpo_texto = f"""
Olá, {nome}!

Obrigado por se cadastrar no PETDor.

Para ativar sua conta, confirme seu e-mail clicando no link abaixo:

{link}

Se você não criou esta conta, apenas ignore este e-mail.

Equipe PETDor.
"""

        corpo_html = f"""
<html>
<body>
    <p>Olá, <b>{nome}</b>!</p>
    <p>Obrigado por se cadastrar no PETDor.</p>
    <p>Para ativar sua conta, clique no botão abaixo:</p>

    <p>
        <a href="{link}" 
           style="padding: 10px 18px; background:#4CAF50; color:white; 
                  border-radius:6px; text-decoration:none;">
           Confirmar E-mail
        </a>
    </p>

    <p>Se você não criou esta conta, ignore este e-mail.</p>
    <p>Equipe PETDor.</p>
</body>
</html>
"""

        # 5 — Enviar o e-mail
        ok_email, msg_email = enviar_email_confirmacao_generico(
            destinatario_email=email,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=corpo_texto
        )

        if not ok_email:
            logger.error(f"[CONF-EMAIL] Falha ao enviar: {msg_email}")
            return False, "Erro ao enviar e-mail de confirmação."

        logger.info(f"[CONF-EMAIL] Enviado para {email} (ID {user_id})")
        return True, "E-mail de confirmação enviado com sucesso."

    except Exception as e:
        logger.exception(f"Erro ao enviar e-mail de confirmação para {email}")
        return False, f"Erro interno ao enviar e-mail: {e}"


# =====================================================================
# 2. VALIDAR TOKEN DE CONFIRMAÇÃO
# =====================================================================
def confirmar_email_com_token(token: str) -> Tuple[bool, str]:
    """
    Valida token JWT e marca o usuário como confirmado no banco.
    """

    try:
        payload, erro_validacao = validar_token_confirmacao_email(token)

        if not payload:
            return False, erro_validacao

        email = payload.get("email")
        user_id = payload.get("user_id")

        if not email or not user_id:
            return False, "Token inválido."

        # Busca usuário
        ok_user, usuario_db = buscar_usuario_por_email(email)

        if not ok_user or not usuario_db:
            return False, "Usuário não encontrado."

        if usuario_db.get("id") != user_id:
            return False, "Token não pertence ao usuário."

        # Verifica consistência do token com o banco
        if usuario_db.get("email_confirm_token") != token:
            return False, "Token já utilizado ou inválido."

        # Marca como confirmado
        ok_confirma, msg_confirma = marcar_email_como_confirmado(email)

        if not ok_confirma:
            return False, msg_confirma

        logger.info(f"[CONF-EMAIL] E-mail {email} confirmado com sucesso.")
        return True, "Seu e-mail foi confirmado com sucesso!"

    except Exception as e:
        logger.exception(f"Erro ao confirmar e-mail com token.")
        return False, f"Erro interno ao confirmar e-mail: {e}"


__all__ = [
    "enviar_email_confirmacao",
    "confirmar_email_com_token",
]
