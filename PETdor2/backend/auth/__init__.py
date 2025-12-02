# PetDor2/backend/auth/__init__.py
"""
Módulo de autenticação e gerenciamento de usuários do PETDor.
Exponha aqui as funções e classes principais dos submódulos.
"""

# Importações relativas dentro do pacote 'auth'
from .user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    atualizar_usuario,
    atualizar_tipo_usuario,
    atualizar_status_usuario,
    alterar_senha,
    deletar_usuario,
    marcar_email_como_confirmado,
)

from .password_reset import (
    solicitar_reset_senha,
    validar_token_reset, # Renomeado para validar_token_reset_senha em security.py
    redefinir_senha_com_token,
    limpar_tokens_reset_expirados,
)

from .email_confirmation import (
    confirmar_email_com_token,
    enviar_email_confirmacao, # Adicionado para ser acessível
)

from .security import (
    hash_password, # Nomes atualizados
    verify_password, # Nomes atualizados
    gerar_token_jwt,
    validar_token_jwt,
    gerar_token_reset_senha,
    validar_token_reset_senha,
    gerar_token_confirmacao_email,
    validar_token_confirmacao_email,
    usuario_logado,
    logout,
)

__all__ = [
    # user.py
    "cadastrar_usuario",
    "verificar_credenciais",
    "buscar_usuario_por_id",
    "buscar_usuario_por_email",
    "atualizar_usuario",
    "atualizar_tipo_usuario",
    "atualizar_status_usuario",
    "alterar_senha",
    "deletar_usuario",
    "marcar_email_como_confirmado",

    # password_reset.py
    "solicitar_reset_senha",
    "validar_token_reset", # Manter para compatibilidade se usado em outro lugar
    "redefinir_senha_com_token",
    "limpar_tokens_reset_expirados",

    # email_confirmation.py
    "confirmar_email_com_token",
    "enviar_email_confirmacao",

    # security.py
    "hash_password",
    "verify_password",
    "gerar_token_jwt",
    "validar_token_jwt",
    "gerar_token_reset_senha",
    "validar_token_reset_senha",
    "gerar_token_confirmacao_email",
    "validar_token_confirmacao_email",
    "usuario_logado",
    "logout",
]
