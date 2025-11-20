# PETdor_2.0/auth/__init__.py
"""
Módulo de autenticação e gerenciamento de usuários para o PETDor.
Contém funcionalidades para cadastro, login, redefinição de senha e segurança.
"""

# Não importamos os módulos aqui para evitar ciclos.
# Eles serão importados diretamente onde forem necessários (ex: em petdor.py).

# Definimos __all__ para indicar o que faz parte do pacote,
# mas sem carregar os módulos imediatamente.
__all__ = [
    "user",
    "password_reset",
    "email_confirmation",
    "security",
]
