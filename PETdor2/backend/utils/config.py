# PETdor2/backend/utils/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
# Isso é importante para que os.getenv() funcione corretamente em ambiente local
# No Streamlit Cloud, as variáveis de ambiente são injetadas diretamente,
# então esta linha não terá efeito lá, mas é boa prática para desenvolvimento local.
load_dotenv()

# ================================
# CAMINHOS E CONFIGURAÇÕES GERAIS
# ================================

# Caminho raiz do projeto (assumindo que config.py está em backend/utils/)
# Volta 2 níveis: utils/ -> backend/ -> PETdor2/
# Se a estrutura for PETdor2/backend/utils/config.py e a raiz for PETdor2/, então:
# ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# No entanto, se a raiz para imports for 'backend', e 'utils' está dentro de 'backend',
# e você quer que ROOT_DIR seja a pasta 'backend', então:
ROOT_DIR = Path(__file__).resolve().parent.parent # Volta 1 nível (utils -> backend)

# Configuração do banco de dados (se você ainda estiver usando SQLite localmente)
# Se estiver usando apenas Supabase, esta parte pode ser removida ou adaptada.
DATABASE_FILE = "petdor.db"
DATABASE_PATH = str(ROOT_DIR / "database" / DATABASE_FILE) # Assumindo database/ está em backend/

# Informações gerais do aplicativo
APP_CONFIG = {
    "titulo": "PETDOR",
    "versao": "1.0.0",
    "autor": "Salute Vitae AI",
}

# ================================
# CONFIGURAÇÕES DO SUPABASE
# ================================
# Estas variáveis são lidas diretamente dos Environment Variables do Streamlit Cloud
# ou do seu arquivo .env local.

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Se você ainda estiver usando conexão direta com PostgreSQL (psycopg2),
# estas variáveis seriam necessárias. Como estamos focando na API REST,
# elas podem ser removidas se não forem mais usadas no código.
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ================================
# CONFIGURAÇÕES DE E-MAIL (SMTP)
# ================================
# As variáveis abaixo são lidas diretamente do ambiente
# (ideal para Streamlit Cloud e desenvolvimento local com .env)

SMTP_SERVIDOR = os.getenv("EMAIL_HOST", "smtpout.secureserver.net")
SMTP_PORTA = int(os.getenv("EMAIL_PORT", "587"))
SMTP_REMETENTE = os.getenv("EMAIL_SENDER", "relatorio@petdor.app") # Quem envia o e-mail
SMTP_EMAIL = os.getenv("EMAIL_USER", "relatorio@petdor.app")     # Usuário para autenticação SMTP
SMTP_SENHA = os.getenv("EMAIL_PASSWORD", "")                      # Senha para autenticação SMTP
SMTP_USAR_SSL = os.getenv("EMAIL_USE_SSL", "True").lower() == "true" # Se deve usar SSL/TLS (True/False)

# ================================
# CONFIGURAÇÕES DE SEGURANÇA
# ================================
# Chave secreta para tokens JWT (confirmação de e-mail, reset de senha)
SECRET_KEY = os.getenv("SECRET_KEY")

# ================================
# CONFIGURAÇÕES DO APP STREAMLIT
# ================================
STREAMLIT_APP_URL = os.getenv("STREAMLIT_APP_URL", "https://petdor.streamlit.app")
