"""
Pacote utilitário do PETDor2.
Expondo funções e helpers gerais de forma explícita.
"""

# ==============================
# Importações diretas de módulos que não causam circularidade
# ==============================
from .validators import validar_email, validar_cpf
from .notifications import enviar_email, enviar_sms
from .utils import gerar_token, formatar_data
from .config import CONFIG, EMAIL_SETTINGS

# ==============================
# Funções que dependem de backend.petdor (import local para evitar circularidade)
# ==============================
def format_pet_nome_local(pet):
    from backend.petdor import format_pet_nome
    return format_pet_nome(pet)

def calcular_idade_pet_local(data_nascimento):
    from backend.petdor import calcular_idade_pet
    return calcular_idade_pet(data_nascimento)

# ==============================
# Exportações explícitas
# ==============================
__all__ = [
    "format_pet_nome_local",
    "calcular_idade_pet_local",
    "validar_email",
    "validar_cpf",
    "enviar_email",
    "enviar_sms",
    "gerar_token",
    "formatar_data",
    "CONFIG",
    "EMAIL_SETTINGS",
]
