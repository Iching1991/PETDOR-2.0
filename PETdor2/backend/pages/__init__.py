"""
Pacote de páginas da aplicação PETDor2.
Organiza e disponibiliza todas as páginas do Streamlit.
"""

from . import login
from . import cadastro
from . import cadastro_pet
from . import avaliacao
from . import admin
from . import home
from . import confirmar_email
from . import conta
from . import historico
from . import password_reset
from . import recuperar_senha

__all__ = [
    "login",
    "cadastro",
    "cadastro_pet",
    "avaliacao",
    "admin",
    "home",
    "confirmar_email",
    "conta",
    "historico",
    "password_reset",
    "recuperar_senha",
]
