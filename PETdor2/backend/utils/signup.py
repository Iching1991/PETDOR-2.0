import streamlit as st
import sqlite3
import bcrypt
from utils.email_sender import enviar_email_confirmacao

# ---------------------------
# Função auxiliar para conectar ao banco
# ---------------------------
def get_conn():
    return sqlite3.connect("database.db", check_same_thread=False)


# ---------------------------
# Função principal de cadastro
# ---------------------------
def signup_page():
    st.title("Cadastro de Usuário")
    st.write("Crie sua conta para acessar o sistema PETdor")

    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo:")
        email = st.text_input("E-mail:")
        senha = st.text_input("Senha:", type="password")
        senha2 = st.text_input("Confirmar senha:", type="password")

        tipo_usuario = st.selectbox(
            "Tipo de usuário:",
            ["Tutor", "Veterinário", "Clínica"]
        )

        pais = st.selectbox(
            "País onde está se cadastrando:",
            ["Brasil", "Argentina", "Chile", "México", "EUA", "Canadá", "Portugal", "Espanha", "Outro"]
        )

        enviar = st.form_submit_button("Criar conta")

    if enviar:
        # ---------------------------
        # Validações
        # ---------------------------
        if not nome or not email or not senha:
            st.error("Preencha todos os campos obrigatórios.")
            return

        if senha != senha2:
            st.error("As senhas não coincidem.")
            return

        conn = get_conn()
        cursor = conn.cursor()

        # Verifica se email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            st.error("Este e-mail já está cadastrado.")
            conn.close()
            return

        # ---------------------------
        # Gera hash da senha
        # ---------------------------
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

        # ---------------------------
        # Insere usuário
        # ---------------------------
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirmado)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (nome, email, senha_hash, tipo_usuario, pais))

        conn.commit()
        conn.close()

        # ---------------------------
        # Envia e-mail de confirmação
        # ---------------------------
        try:
            enviar_email_confirmacao(email, nome)
            st.success("Conta criada! Verifique seu e-mail para confirmar.")
        except Exception as e:
            st.warning(f"Conta criada, mas houve erro ao enviar e-mail: {str(e)}")


# Página pode ser chamada em login.py ou diretamente
def main():
    signup_page()


if __name__ == "__main__":
    main()
