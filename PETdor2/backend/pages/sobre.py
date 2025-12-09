# backend/pages/sobre.py
"""
Página 'Sobre' do PETDor2.
Exibe informações sobre o projeto, propósito e equipe.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)

def render():
    """Renderiza a página Sobre o Projeto."""
    st.title("ℹ️ Sobre o PETDor")

    st.markdown("""
    ## 🐾 O que é o PETDor?

    O **PETDor** é uma plataforma criada para auxiliar tutores e profissionais de saúde animal
    na **avaliação da dor em animais**, utilizando escalas científicas adaptadas para cada espécie.

    Nosso objetivo é fornecer uma ferramenta simples, rápida e confiável para apoiar decisões clínicas 
    e melhorar o bem-estar dos pets.

    ---

    ## 🧪 Tecnologias Utilizadas
    - Python 3.13  
    - Streamlit  
    - Supabase (Banco de Dados e Autenticação)
    - JWT para criação de tokens
    - API REST integrada

    ---

    ## 👥 Criador
    **Agnaldo Baldissera**  
    Desenvolvedor e idealizador do PETDor.

    ---

    ## 📬 Contato
    Se tiver dúvidas ou sugestões:
    - 📧 Email: suporte@petdor.com
    - 🌐 Site: https://petdor.com
    """)

__all__ = ["render"]
