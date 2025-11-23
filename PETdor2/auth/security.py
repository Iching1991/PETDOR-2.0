# PETdor2/auth/security.py
import os
import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

logger = logging.getLogger(__name__)

# ==========================================================
# Chave secreta segura
# ==========================================================
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

if not SECRET_KEY or len(SECRET_KEY) < 32:
    logger.warning(
        "⚠ SECRET_KEY fraca ou ausente! "
        "Use uma chave forte (32+ chars) em produção."
    )
    SECRET_KEY = SECRET_KEY or "dev-secret-key-change-this-please"


# ==========================================================
# Hash de senha
# ==========================================================
def hash_password(password: str) -> str:
    """Retorna hash seguro com bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Valida senha comparando com hash bcrypt."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# ==========================================================
# Função genérica para criar JWT seguro
# ==========================================================
def _generate_jwt(email: str, token_type: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "type": token_type,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _verify_jwt(token: str, expected_type: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != expected_type:
            logger.debug(f"Tipo de token incorreto: {payload.get('type')}")
            return None

        return payload.get("sub")

    except jwt.ExpiredSignatureError:
        logger.debug(f"Token '{expected_type}' expirado.")
        return None
    except jwt.InvalidTokenError:
        logger.debug(f"Token '{expected_type}' inválido.")
        return None


# ==========================================================
# Token de confirmação de e-mail
# ==========================================================
def generate_email_token(email: str, expires_minutes: int = 60 * 24) -> str:
    """Token JWT válido por padrão 24h."""
    return _generate_jwt(email, "email_confirmation", expires_minutes)


def verify_email_token(token: str) -> str | None:
    """Retorna o e-mail se o token for válido."""
    return _verify_jwt(token, "email_confirmation")


# ==========================================================
# Token de reset de senha
# ==========================================================
def generate_reset_token(email: str, expires_minutes: int = 60) -> str:
    """Token JWT para reset (padrão 1h)."""
    return _generate_jwt(email, "password_reset", expires_minutes)


def verify_reset_token(token: str) -> str | None:
    """Valida token de reset e retorna o e-mail, se válido."""
    return _verify_jwt(token, "password_reset")
