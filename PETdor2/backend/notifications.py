# PetDor/utils/notifications.py

import logging

logger = logging.getLogger("PETDOR_NOTIFICATIONS")

def enviar_notificacao(destinatario: str, mensagem: str):
    """
    Envia uma notificação simples (log interno).
    Futuramente pode ser conectado a email, SMS, WhatsApp, etc.
    """
    try:
        logger.info(f"Notificação para {destinatario}: {mensagem}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")
        return False
