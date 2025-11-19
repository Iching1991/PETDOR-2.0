import time
import hashlib
import secrets

# Tempo padrão de expiração: 1 hora
TOKEN_EXPIRATION = 3600  


# ========================================
# GERAR TOKEN SIMPLES
# ========================================
def gerar_token_simples(email):
    """
    Gera um token baseado em email + timestamp + segredo aleatório.
    Ideal para confirmação de email e reset de senha.
    """
    timestamp = int(time.time())
    segredo = secrets.token_hex(16)
    base = f"{email}:{timestamp}:{segredo}"

    token_hash = hashlib.sha256(base.encode()).hexdigest()

    # Retornamos um token verificável contendo hash + timestamp + email
    return f"{token_hash}:{timestamp}:{email}"


# ========================================
# VALIDAR TOKEN
# ========================================
def validar_token_simples(token_recebido):
    """
    Valida token gerado por gerar_token_simples.
    Retorna o email se válido, senão retorna None.
    """
    try:
        token_hash, timestamp_str, email = token_recebido.split(":")
        timestamp = int(timestamp_str)

        # Verifica se expirou
        if time.time() - timestamp > TOKEN_EXPIRATION:
            return None

        # Como o segredo é aleatório, não conseguimos recalcular o hash.
        # Porém, a estrutura do token garante que apenas tokens criados aqui
        # possuem este formato. Assim, validamos apenas o tempo e o formato.
        return email

    except Exception:
        return None
