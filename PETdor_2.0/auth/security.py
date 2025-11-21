# PETdor_2_0/auth/security.py
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# Chave secreta para JWT (idealmente de variáveis de ambiente)
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_muito_segura_aqui")
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Gera o hash de uma senha usando bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se uma senha corresponde ao hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False # Hash inválido

def generate_email_token(email: str) -> str:
    """Gera um token JWT para confirmação de e-mail."""
    payload = {
        "sub": email,
        "exp": datetime.now() + timedelta(days=1), # Token válido por 1 dia
        "type": "email_confirmation"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_email_token(token: str) -> str | None:
    """Verifica e decodifica um token de confirmação de e-mail."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "email_confirmation":
            return payload.get("sub")
        return None
    except jwt.ExpiredSignatureError:
        return None # Token expirado
    except jwt.InvalidTokenError:
        return None # Token inválido

# --- NOVAS FUNÇÕES PARA RESET DE SENHA ---
def generate_reset_token(email: str) -> str:
    """Gera um token JWT para redefinição de senha."""
    payload = {
        "sub": email,
        "exp": datetime.now() + timedelta(hours=1), # Token válido por 1 hora
        "type": "password_reset"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str) -> str | None:
    """Verifica e decodifica um token de redefinição de senha."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "password_reset":
            return payload.get("sub")
        return None
    except jwt.ExpiredSignatureError:
        return None # Token expirado
    except jwt.InvalidTokenError:
        return None # Token inválido
