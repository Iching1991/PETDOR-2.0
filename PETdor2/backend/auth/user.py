# PetDor2/backend/auth/security.py
"""
Módulo de segurança do PETDor:
- hash e verificação de senha (bcrypt)
- geração e validação de JWT (PyJWT)
- helpers para tokens específicos (reset de senha, confirmação de e-mail)
- helpers de sessão para Streamlit (usuario_logado, logout)
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

logger = logging.getLogger(__name__)

# Leitura segura da chave: preferir secrets do Streamlit / .env em produção
SECRET_KEY = os.getenv("SECRET_KEY", "troque_esta_chave_em_producao")
ALGORITHM = "HS256"


# ---------------------------
# Hashing de senha (bcrypt)
# ---------------------------
def hash_password(senha: str) -> str:
    """Gera hash bcrypt da senha (utf-8)."""
    if senha is None:
        raise ValueError("Senha não pode ser None")
    hashed = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(senha: str, senha_hash: str) -> bool:
    """Verifica senha contra hash (retorna False em erro)."""
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except Exception as e:
        logger.exception("Erro ao verificar senha")
        return False


# ---------------------------
# JWT genérico
# ---------------------------
def gerar_token_jwt(payload: Dict[str, Any], expiracao_horas: int = 1) -> str:
    """Gera JWT com claims do payload e campos iat/exp UTC-aware."""
    now = datetime.now(timezone.utc)
    claims = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=expiracao_horas)).timestamp())
    }
    token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
    # PyJWT 2.x returns str
    return token


def validar_token_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Retorna payload decodificado ou None se inválido/expirado."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Token inválido")
        return None
    except Exception:
        logger.exception("Erro ao validar token JWT")
        return None


# ---------------------------
# Token reset de senha
# ---------------------------
def gerar_token_reset_senha(usuario_id: int, email: str) -> str:
    """Gera token JWT para reset de senha — payload padronizado."""
    payload = {"tipo": "reset_senha", "usuario_id": usuario_id, "email": email}
    return gerar_token_jwt(payload, expiracao_horas=1)  # 1 hora


def validar_token_reset_senha(token: str) -> Optional[Dict[str, Any]]:
    """Valida token de reset e garante o campo 'tipo' correto. Retorna payload ou None."""
    payload = validar_token_jwt(token)
    if not payload:
        return None
    if payload.get("tipo") != "reset_senha":
        logger.warning("Token não é do tipo reset_senha")
        return None
    return payload


# ---------------------------
# Token confirmação de e-mail
# ---------------------------
def gerar_token_confirmacao_email(usuario_id: int, email: str) -> str:
    """Gera token JWT para confirmação de e-mail — expira em 24h."""
    payload = {"tipo": "confirmacao_email", "user_id": usuario_id, "email": email}
    return gerar_token_jwt(payload, expiracao_horas=24)


def validar_token_confirmacao_email(token: str) -> Optional[Dict[str, Any]]:
    """Valida token de confirmação de e-mail; retorna payload ou None."""
    payload = validar_token_jwt(token)
    if not payload:
        return None
    if payload.get("tipo") != "confirmacao_email":
        logger.warning("Token não é do tipo confirmacao_email")
        return None
    return payload


# ---------------------------
# Helpers para Streamlit
# ---------------------------
def usuario_logado(session_state) -> bool:
    """Verifica se existe user_id na session_state."""
    return bool(session_state.get("user_id"))


def logout(session_state) -> None:
    """Limpa chaves de sessão relacionadas ao login."""
    for k in ("user_id", "user_data", "user_email", "user_name", "is_admin"):
        if k in session_state:
            del session_state[k]
    # opcional: set page/login
    session_state["page"] = "Login"
    logger.info("Usuário deslogado (session_state limpo)")


# Export
__all__ = [
    "hash_password",
    "verify_password",
    "gerar_token_jwt",
    "validar_token_jwt",
    "gerar_token_reset_senha",
    "validar_token_reset_senha",
    "gerar_token_confirmacao_email",
    "validar_token_confirmacao_email",
    "usuario_logado",
    "logout",
]
