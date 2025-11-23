# PETdor2/utils/tokens.py

"""
Módulo unificado de tokens para o PETdor2.
Gera e valida tokens JWT para:
- Confirmação de e-mail
- Redefinição de senha
"""

import os
from datetime import datetime, timedelta
import jwt

# Chave secreta (use variável de ambiente em produção)
SECRET_KEY = os.getenv("SECRET_KEY", "chave_super_secreta_petdor")
ALGORITHM = "HS256"

# Expirações
EMAIL_TOKEN_EXPIRE_HOURS = 24
RESET_TOKEN_EXPIRE_HOURS = 1


# ==========================================================
# GERAR TOKEN DE CONFIRMAÇÃO DE E-MAIL
# ==========================================================
def gerar_token_confirmacao(email: str) -> str:
    payload = {
        "sub": email,
        "type": "email_confirmation",
        "exp": datetime.utcnow() + timedelta(hours=EMAIL_TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================================
# VALIDAR TOKEN DE CONFIRMAÇÃO DE E-MAIL
# ==========================================================
def validar_token_confirmacao(token: str) -> str | None:
    try:
        dados = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if dados.get("type") != "email_confirmation":
            return None
        return dados.get("sub")
    except Exception:
        return None


# ==========================================================
# GERAR TOKEN DE RESET DE SENHA
# ==========================================================
def gerar_token_reset(email: str) -> str:
    payload = {
        "sub": email,
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================================
# VALIDAR TOKEN DE RESET DE SENHA
# ==========================================================
def validar_token_reset(token: str) -> str | None:
    try:
        dados = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if dados.get("type") != "password_reset":
            return None
        return dados.get("sub")
    except Exception:
        return None
