# PETdor2/auth/__init__.py
"""
Pacote de autenticação - gerencia login, registro e segurança.
Módulos:
  - user: funções de verificação e cadastro de usuários
  - security: hash de senhas e tokens JWT
  - password_reset: recuperação de senha
  - email_confirmation: confirmação de e-mail
"""
from . import user
from . import security
from . import password_reset
from . import email_confirmation

__all__ = [
    "user",
    "security",
    "password_reset",
    "email_confirmation",
]
