# PETdor_2.0/auth/__init__.py
"""
Módulo de autenticação e gerenciamento de usuários para o PETDor.
Contém funcionalidades para cadastro, login, redefinição de senha e segurança.
"""

# Importa os módulos principais para serem acessíveis diretamente via 'auth.user', 'auth.security', etc.
from . import user
from . import password_reset
from . import email_confirmation
from . import security

# Define quais módulos são expostos quando 'from auth import *' é usado
__all__ = [
    "user",
    "password_reset",
    "email_confirmation",
    "security",
]
