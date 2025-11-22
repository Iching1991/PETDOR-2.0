# PetDor/pages/cadastro.py
import streamlit as st
from auth.user import cadastrar_usuario

def app():
    st.header("📝 Criar Conta")

    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    pais = st.selectbox("País", ["Brasil", "Portugal", "EUA", "Outro"])
    tipo = st.selectbox("Tipo de conta", ["Tutor", "Veterinário", "Clínica"])

    if st.button("Criar Conta"):
        ok, msg = cadastrar_usuario(nome, email, senha, confirmar)
        if ok:
            st.success(msg + " — verifique seu e-mail para confirmar (se configurado).")
        else:
            st.error(msg)

    st.markdown("""
    **Observações:**  
    - Ao criar conta como *Veterinário* ou *Clínica* você poderá adicionar informações adicionais no perfil (CRMV / CNPJ) via página **Conta**.
    - O campo país é meramente informativo e pode ser usado para localizações futuras.
    """)
