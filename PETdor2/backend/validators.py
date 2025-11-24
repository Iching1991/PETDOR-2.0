# PETdor_2.0/utils/validators.py

"""
Módulo para funções de validação de dados, como e-mails e senhas.
"""
import re

def validar_email(email: str) -> bool:
    """
    Valida o formato de um endereço de e-mail.
    """
    # Regex simples para validação de e-mail
    # Pode ser mais complexo dependendo dos requisitos
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(regex, email) is not None

def validar_senha(senha: str) -> bool:
    """
    Valida a força de uma senha.
    Requisitos:
    - Mínimo de 8 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    """
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Z]", senha): # Pelo menos uma maiúscula
        return False
    if not re.search(r"[a-z]", senha): # Pelo menos uma minúscula
        return False
    if not re.search(r"\d", senha):    # Pelo menos um número
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha): # Pelo menos um caractere especial
        return False
    return True

# Você pode adicionar outras funções de validação aqui, se necessário.
