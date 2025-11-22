# PetDor/utils/validators.py

import re

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

def validar_email(email: str) -> bool:
    """
    Valida formato de email.
    """
    if not email:
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))

def validar_senha(senha: str) -> bool:
    """
    Valida se a senha atende critérios mínimos.
    
    Critérios:
    - mínimo 8 caracteres
    - 1 letra maiúscula
    - 1 letra minúscula
    - 1 número
    - 1 caractere especial
    """
    if not senha or len(senha) < 8:
        return False

    regras = [
        r"[A-Z]",  # maiúscula
        r"[a-z]",  # minúscula
        r"[0-9]",  # número
        r"[^A-Za-z0-9]",  # símbolo
    ]

    return all(re.search(regra, senha) for regra in regras)

def sanitize_text(text: str) -> str:
    """
    Remove espaços desnecessários, múltiplos espaços e caracteres perigosos.
    """
    if not isinstance(text, str):
        return ""

    # remove espaços duplicados
    text = re.sub(r"\s+", " ", text)

    # remove caracteres suspeitos
    text = re.sub(r"[<>;{}$]", "", text)

    return text.strip()
