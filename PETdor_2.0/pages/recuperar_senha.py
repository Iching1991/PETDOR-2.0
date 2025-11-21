import streamlit as st
from auth.password_reset import solicitar_reset_senha

st.set_page_config(page_title="Recuperar Senha - PETDor")


def main():
    st.title("🔐 Recuperar Senha")

    st.write(
        "Digite o e-mail que você usou para criar sua conta no **PETDor**. "
        "Se ele existir no sistema, enviaremos um link para redefinir sua senha."
    )

    email = st.text_input("📧 E-mail cadastrado")

    if st.button("Enviar link de recuperação"):
        if not email or "@" not in email:
            st.error("Digite um e-mail válido.")
            return

        try:
            ok = solicitar_reset_senha(email)

            # Segurança: não revelar se o email existe
            if ok:
                st.success(
                    "Se o e-mail existir no sistema, enviamos um link de recuperação. "
                    "Verifique sua caixa de entrada e o spam."
                )
            else:
                # Mesmo comportamento, para evitar revealing accounts
                st.success(
                    "Se o e-mail existir no sistema, enviamos um link de recuperação. "
                    "Verifique sua caixa de entrada e o spam."
                )

        except Exception as e:
            st.error("⚠ Ocorreu um erro ao processar a solicitação. Tente novamente.")
            st.exception(e)


if __name__ == "__main__":
    main()
