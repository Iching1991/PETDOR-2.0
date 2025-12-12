# backend/utils/__init__.py

from .email_sender import (
    enviar_email_confirmacao_generico,
    enviar_email_recuperacao_senha,
)

from .config import (
    SMTP_SERVIDOR,
    SMTP_PORTA,
    SMTP_EMAIL,
    SMTP_SENHA,
    SMTP_USAR_SSL,
    APP_CONFIG,
    STREAMLIT_APP_URL,
    SUPABASE_URL,
    SUPABASE_KEY,
)

__all__ = [
    "enviar_email_confirmacao_generico",
    "enviar_email_recuperacao_senha",
    "SMTP_SERVIDOR",
    "SMTP_PORTA",
    "SMTP_EMAIL",
    "SMTP_SENHA",
    "SMTP_USAR_SSL",
    "APP_CONFIG",
    "STREAMLIT_APP_URL",
    "SUPABASE_URL",
    "SUPABASE_KEY",
]
