"""
Sistema de Recuperação de Senha - PETDOR
----------------------------------------
Fluxo:
1. Usuário solicita recuperação → gera token → salva no banco → envia email
2. Usuário clica no link → valida token
3. Usuário redefine a senha → token é invalidado
"""

import secrets
import hashlib
import sqlite3
from datetime import datetime, timedelta

# Importa função correta de envio de reset de senha
from utils.email_sender import enviar_email_reset_senha

# Caminho do banco local
DB_PATH = "database/petdor.db"


# ============================================================
# 📌 Funções utilitárias internas
# ============================================================

def conectar():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def hash_senha(senha: str) -> str:
    """Hash seguro da senha usando SHA256."""
    return hashlib.sha256(senha.encode()).hexdigest()


# ============================================================
# 📌 1. Solicitar reset (gerar token + email)
# ============================================================

def solicitar_reset_senha(email: str) -> bool:
    """
    Gera token de recuperação, salva no BD e envia e-mail.
    Retorna True se o processo foi iniciado, False caso email não exista.
    """
    conn = conectar()
    cur = conn.cursor()

    # Verifica se email existe
    cur.execute("SELECT id, nome FROM usuarios WHERE email = ?", (email,))
    user = cur.fetchone()

    if not user:
        conn.close()
        return False

    user_id, nome = user

    # Gera token único e define validade de 1 hora
    token = secrets.token_hex(32)
    validade = datetime.utcnow() + timedelta(hours=1)

    # Remove tokens antigos
    cur.execute("DELETE FROM password_resets WHERE user_id = ?", (user_id,))

    # Salva novo token
    cur.execute("""
        INSERT INTO password_resets (user_id, token, validade)
        VALUES (?, ?, ?)
    """, (user_id, token, validade.isoformat()))

    conn.commit()
    conn.close()

    # Envia email com token
    enviar_email_reset_senha(email, nome, token)

    return True


# ============================================================
# 📌 2. Validar token no link
# ============================================================

def validar_token_reset(token: str):
    """
    Retorna user_id se token for válido; caso contrário, retorna None.
    """
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, validade
        FROM password_resets
        WHERE token = ?
    """, (token,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    user_id, validade = row

    # Verifica expiração
    if datetime.utcnow() > datetime.fromisoformat(validade):
        return None

    return user_id


# ============================================================
# 📌 3. Redefinir senha
# ============================================================

def redefinir_senha_com_token(token: str, nova_senha: str) -> bool:
    """
    Altera a senha do usuário caso token seja válido.
    Retorna True se redefiniu, False caso token inválido.
    """
    user_id = validar_token_reset(token)

    if not user_id:
        return False

    conn = conectar()
    cur = conn.cursor()

    nova_hash = hash_senha(nova_senha)

    # Atualiza senha
    cur.execute("""
        UPDATE usuarios
        SET senha = ?
        WHERE id = ?
    """, (nova_hash, user_id))

    # Invalida token
    cur.execute("DELETE FROM password_resets WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()
    return True


