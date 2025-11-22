# config.py
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DATABASE_FILE = "petdor.db" # nome do arquivo dentro da pasta database/
DATABASE_PATH = str(ROOT_DIR / "database" / DATABASE_FILE)


APP_CONFIG = {
"titulo": "PETDOR",
"versao": "1.0.0",
"autor": "Salute Vitae AI",
}


# Email (ajuste conforme seu provedor)
EMAIL_CONFIG = {
"smtp_server": os.getenv("EMAIL_SMTP", "smtpout.secureserver.net"),
"smtp_port": int(os.getenv("EMAIL_PORT", "587")),
"remetente": os.getenv("EMAIL_FROM", "relatorio@petdor.app"),
"usuario": os.getenv("EMAIL_USER", "relatorio@petdor.app"),
"senha": os.getenv("EMAIL_PASSWORD", ""),
}
