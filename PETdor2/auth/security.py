# PETdor2/auth/security.py
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_muito_segura") # Use uma chave forte em produção!
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Gera o hash de uma senha."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se uma senha corresponde ao hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_email_token(email: str, expires_delta_minutes: int = 60) -> str:
    """Gera um token JWT para confirmação de e-mail."""
    expire = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)
    to_encode = {"exp": expire, "sub": email, "type": "email_confirm"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_email_token(token: str) -> str | None:
    """Verifica um token JWT de confirmação de e-mail e retorna o e-mail se válido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "email_confirm":
            return payload.get("sub")
        return None
    except jwt.ExpiredSignatureError:
        logger.warning("Token de confirmação de e-mail expirado.")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Token de confirmação de e-mail inválido.")
        return None

# Funções para reset de senha (padronizando nomes)
def generate_reset_token(email: str, expires_delta_minutes: int = 30) -> str:
    """Gera um token JWT para reset de senha."""
    expire = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)
    to_encode = {"exp": expire, "sub": email, "type": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_reset_token(token: str) -> str | None:
    """Verifica um token JWT de reset de senha e retorna o e-mail se válido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "password_reset":
            return payload.get("sub")
        return None
    except jwt.ExpiredSignatureError:
        logger.warning("Token de reset de senha expirado.")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Token de reset de senha inválido.")
        return None


