import os
from pathlib import Path

# Caminho raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent  # volta 1 nível (utils → raiz)

# Configuração do banco de dados
DATABASE_FILE = "petdor.db"
DATABASE_PATH = str(ROOT_DIR / "database" / DATABASE_FILE)

# Informações gerais do aplicativo
APP_CONFIG = {
    "titulo": "PETDOR",
    "versao": "1.0.0",
    "autor": "Salute Vitae AI",
}

# ================================
# CONFIGURAÇÕES DE E-MAIL
# ================================
# As variáveis abaixo podem ser configuradas no ambiente
# (ideal para Streamlit Cloud, pois você pode esconder a senha)

EMAIL_CONFIG = {
    "smtp_server": os.getenv("EMAIL_SMTP", "smtpout.secureserver.net"),
    "smtp_port": int(os.getenv("EMAIL_PORT", "587")),
    "remetente": os.getenv("EMAIL_FROM", "relatorio@petdor.app"),
    "usuario": os.getenv("EMAIL_USER", "relatorio@petdor.app"),
    "senha": os.getenv("EMAIL_PASSWORD", ""),
}
