# utils/signup.py

import logging
import sqlite3
import bcrypt

from utils.validators import validar_email, validar_senha
from utils.tokens import gerar_token_verificacao
from utils.email_sender import enviar_email_verificacao

logger = logging.getLogger(__name__)


# ---------------------------
# Conexão com banco
# ---------------------------
def get_conn():
    return sqlite3.connect("database.db", check_same_thread=False)


# ---------------------------
# Função principal de cadastro
# ---------------------------
def cadastrar_usuario(nome, email, senha, tipo_usuario, pais):
    """
    Função central de cadastro, usada pela página Streamlit.
    Faz:
    - validações
    - hash da senha
    - gravação no banco
    - geração de token
    - envio de email
    """

    # --------- Validações ---------
    if not nome or not email or not senha:
        return False, "Preencha todos os campos obrigatórios."

    if not validar_email(email):
        return False, "E-mail inválido."

    if not validar_senha(senha):
        return False, "A senha deve ter pelo menos 6 caracteres."

    conn = get_conn()
    cur = conn.cursor()

    # --------- Verifica duplicidade ---------
    cur.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return False, "Este e-mail já está cadastrado."

    # --------- Hash da senha ---------
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

    # --------- Geração do token ---------
    token = gerar_token_verificacao()

    # --------- Inserção ---------
    cur.execute(
        """
        INSERT INTO usuarios 
        (nome, email, senha_hash, tipo_usuario, pais, email_confirmado, token_verificacao)
        VALUES (?, ?, ?, ?, ?, 0, ?)
        """,
        (nome, email, senha_hash, tipo_usuario, pais, token)
    )

    conn.commit()
    conn.close()

    # --------- E-mail ---------
    try:
        enviar_email_verificacao(email, token)
    except Exception as e:
        logger.error("Erro ao enviar e-mail: %s", e)
        return True, "Conta criada, mas houve erro ao enviar o e-mail de confirmação."

    return True, "Conta criada com sucesso! Verifique seu e-mail."


