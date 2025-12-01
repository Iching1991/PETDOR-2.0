# PetDor2/auth/email_confirmation.py
"""
Módulo de confirmação de e-mail do PETDor
Migrado de SQLite para Supabase + JWT.
"""

import logging
from typing import Tuple

# Importações do novo sistema Supabase + JWT
from database.supabase_client import supabase_table_select, supabase_table_update
from auth.security import gerar_token_confirmacao_email, validar_token_confirmacao_email
from utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"

# ----------------------------------------------
# 1) Gerar token JWT e enviar e-mail de confirmação
# ----------------------------------------------
def enviar_email_confirmacao(email: str, nome: str, user_id: int) -> bool:
    """
    Gera token JWT, salva no banco e envia link de confirmação.
    """
    try:
        # Gera token JWT (melhor que UUID simples)
        token = gerar_token_confirmacao_email(email, user_id)

        # Salva token no Supabase (substitui INSERT em email_confirmacoes)
        dados_update = {
            "email_confirm_token": token,
            "atualizado_em": datetime.now().isoformat()
        }

        ok_update, _ = supabase_table_update(
            TABELA_USUARIOS, 
            dados_update, 
            {"id": user_id}
        )

        if not ok_update:
            logger.error(f"Erro ao salvar token de confirmação para usuário {user_id}")
            return False

        # Link de verificação para Streamlit
        link = f"https://petdor.streamlit.app/confirmar_email?token={token}"

        assunto = "Confirme seu e-mail - PETDor"
        mensagem = f"""
Olá, {nome}!

Obrigado por se cadastrar no PETDor.

Para ativar sua conta, confirme seu e-mail clicando no link abaixo:

🔗 {link}

Se você não criou esta conta, apenas ignore este e-mail.

Equipe PETDor.
"""

        # Envia e-mail
        sucesso_email = enviar_email_confirmacao(email, nome, token)  # Ajuste conforme sua função
        if sucesso_email:
            logger.info(f"✅ E-mail de confirmação enviado para {email} (usuário {user_id})")
            return True
        else:
            logger.error(f"❌ Falha ao enviar

