# PETdor2/auth/user.py
"""
Módulo de usuários - autenticação e gerenciamento de contas (SQLite).
"""

import logging
from datetime import datetime
from database.connection import conectar_db
from auth.security import hash_password, verify_password

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# Buscar usuário por e-mail
# ---------------------------------------------------
def buscar_usuario_por_email(email: str) -> dict | None:
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, senha, email_confirmado, ativo, tipo
        FROM usuarios
        WHERE email = ?
    """, (email.lower(),))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    id_, nome, email, senha_hash, confirmado, ativo, tipo = row

    return {
        "id": id_,
        "nome": nome,
        "email": email,
        "senha_hash": senha_hash,
        "email_confirmado": confirmado,
        "ativo": ativo,
        "tipo": tipo,
    }


# ---------------------------------------------------
# Verificar login
# ---------------------------------------------------
def verificar_credenciais(email: str, senha: str) -> tuple[bool, dict]:
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return False, {"erro": "Usuário não encontrado"}

    if not verify_password(senha, usuario["senha_hash"]):
        return False, {"erro": "Senha incorreta"}

    return True, usuario


# ---------------------------------------------------
# Cadastrar usuário
# ---------------------------------------------------
def cadastrar_usuario(nome: str, email: str, senha: str, tipo: str = "tutor") -> tuple[bool, str]:
    conn = conectar_db()
    cursor = conn.cursor()

    # Já existe?
    existente = buscar_usuario_por_email(email)
    if existente:
        return False, "❌ Este e-mail já está cadastrado."

    senha_hash = hash_password(senha)

    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, email_confirmado, ativo, tipo, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nome,
            email.lower(),
            senha_hash,
            False,
            True,
            tipo,
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        return True, "✔ Usuário cadastrado com sucesso! Confirme seu e-mail."

    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}")
        return False, f"❌ Erro ao cadastrar: {str(e)}"

    finally:
        conn.close()


# ---------------------------------------------------
# Atualizar confirmação de e-mail
# ---------------------------------------------------
def confirmar_email(email: str) -> bool:
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios SET email_confirmado = 1
        WHERE email = ?
    """, (email.lower(),))

    conn.commit()
    conn.close()
    return cursor.rowcount > 0


# ---------------------------------------------------
# Redefinir senha
# ---------------------------------------------------
def redefinir_senha(usuario_id: int, nova_senha: str) -> tuple[bool, str]:
    conn = conectar_db()
    cursor = conn.cursor()

    senha_hash = hash_password(nova_senha)

    try:
        cursor.execute("""
            UPDATE usuarios
            SET senha = ?
            WHERE id = ?
        """, (senha_hash, usuario_id))

        conn.commit()
        return True, "✔ Senha redefinida com sucesso!"

    except Exception as e:
        logger.error(f"Erro redefinindo senha: {e}")
        return False, "Erro ao redefinir senha."

    finally:
        conn.close()


# ---------------------------------------------------
# Atualizar status
# ---------------------------------------------------
def atualizar_status_usuario(usuario_id: int, ativo: bool) -> bool:
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET ativo = ?
        WHERE id = ?
    """, (1 if ativo else 0, usuario_id))

    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()

    return ok


# ---------------------------------------------------
# Atualizar tipo
# ---------------------------------------------------
def atualizar_tipo_usuario(usuario_id: int, novo_tipo: str) -> bool:
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET tipo = ?
        WHERE id = ?
    """, (novo_tipo, usuario_id))

    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()

    return ok


__all__ = [
    "buscar_usuario_por_email",
    "verificar_credenciais",
    "cadastrar_usuario",
    "confirmar_email",
    "redefinir_senha",
    "atualizar_status_usuario",
    "atualizar_tipo_usuario",
]
