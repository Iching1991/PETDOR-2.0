# PETdor_2.0/auth/__init__.py

"""
Módulo de inicialização do pacote 'auth'.
Expõe funcionalidades de autenticação e gerenciamento de usuários.
"""
# Importa os submódulos para que possam ser acessados via auth.user, auth.password_reset, etc.
# NUNCA importe funções específicas aqui se elas podem causar um ciclo.
# Apenas importe os módulos.
from . import user
from . import password_reset

__all__ = [
    "user",
    "password_reset",
]

# Se você precisar que funções como 'cadastrar_usuario' sejam acessíveis diretamente
# como 'auth.cadastrar_usuario', você pode adicioná-las aqui DEPOIS que os módulos
# já foram importados e carregados. Mas, para resolver o ciclo atual, é mais seguro
# que o petdor.py importe diretamente de 'auth.user' (o que ele já faz).
