# PETdor2/auth/security.py
import os
import logging
from datetime import datetime, timedelta

import bcrypt
import jwt

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "replace_with_strong_secret_in_production")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Gera o hash de uma senha usando bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se uma senha corresponde ao hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# Email confirmation token (JWT)
def generate_email_token(email: str, expires_minutes: int = 60 * 24) -> str:
    """Gera um JWT para confirmação de e-mail (expira por padrão em 24h)."""
    exp = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": email, "exp": exp, "type": "email_confirmation"}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_email_token(token: str) -> str | None:
    """Retorna email se token válido; caso contrário None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "email_confirmation":
            return payload.get("sub")
        return None
    except jwt.ExpiredSignatureError:
        logger.debug("verify_email_token: token expirado")
        return None
    except jwt.InvalidTokenError:
        logger.debug("verify_email_token: token inválido")
        return None


# Password reset token (JWT short lived)
def generate_reset_token(email: str, expires_minutes: int = 60) -> str:
    """Gera um JWT para redefinição de senha (padrão 60 minutos)."""
    exp = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": email, "exp": exp, "type": "password_reset"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> str | None:
    """Retorna email se token de reset válido; caso contrário None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "password_reset":
            return payload.get("sub")
        return None
    except jwt.ExpiredSignatureError:
        logger.debug("verify_reset_token: token expirado")
        return None
    except jwt.InvalidTokenError:
        logger.debug("verify_reset_token: token inválido")
        return None
