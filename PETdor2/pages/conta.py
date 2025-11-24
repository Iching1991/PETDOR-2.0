# PETdor2/pages/conta.py
"""
Página de gerenciamento de conta do usuário.
Permite atualizar dados pessoais, alterar senha e deletar conta.
"""
import streamlit as st
import logging
from auth.user import (
    buscar_usuario_por_email,
    atualizar_tipo_usuario,
    atualizar_status_usuario,
)
from auth.security import hash_password, verify_password
from database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

def atualizar_dados_usuario(user_id: int, nome: str, email: str) -> tuple[bool, str]:
    """Atualiza nome e email do usuário no banco."""
    try:
        supabase = get_supabase()

        # Verifica se o novo email já está em uso
        if email != st.session_state.usuario.get("email"):
            resp_check = (
                supabase
                .from_("usuarios")
                .select("id")
                .eq("email", email.lower())
                .execute()
            )

            if resp_check.data:
                return False, "❌ Este e-mail já está em uso."

        # Atualiza dados
        response = (
            supabase
            .from_("usuarios")
            .update({
                "nome": nome,
                "email": email.lower()
            })
            .eq("id", user_id)
            .execute()
        )

        if response.data:
            logger.info(f"✅ Dados atualizados para usuário {user_id}")
            return True, "✅ Dados atualizados com sucesso!"
        else:
            return False, "❌ Erro ao atualizar dados."

    except Exception as e:
        logger.error(f"Erro ao atualizar dados: {e}")
        return False, f"❌ Erro: {e}"

def alterar_senha(user_id: int, senha_atual: str, nova_senha: str) -> tuple[bool, str]:
    """Altera a senha do usuário."""
    try:
        supabase = get_supabase()

        # Busca usuário
        response = (
            supabase
            .from_("usuarios")
            .select("senha_hash")
            .eq("id", user_id)
            .single()
            .execute()
        )

        usuario = response.data
        if not usuario:
            return False, "❌ Usuário não encontrado."

        # Verifica senha atual
        if not verify_password(senha_atual, usuario.get("senha_hash", "")):
            return False, "❌ Senha atual incorreta."

        # Valida nova senha
        if len(nova_senha) < 8:
            return False, "❌ Nova senha deve ter pelo menos 8 caracteres."

        if nova_senha == senha_atual:
            return False, "❌ Nova senha não pode ser igual à senha atual."

        # Atualiza senha
        nova_hash = hash_password(nova_senha)

        update_response = (
            supabase
            .from_("usuarios")
            .update({"senha_hash": nova_hash})
            .eq("id", user_id)
            .execute()
        )

        if update_response.data:
            logger.info(f"✅ Senha alterada para usuário {user_id}")
            return True, "✅ Senha alterada com sucesso!"
        else:
            return False, "❌ Erro ao alterar senha."

    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return False, f"❌ Erro: {e}"

def deletar_conta(user_id: int) -> tuple[bool, str]:
    """Deleta a conta do usuário e todos seus dados."""
    try:
        supabase = get_supabase()

        # Deleta avaliações
        supabase.from_("avaliacoes").delete().eq("usuario_id", user_id).execute()

        # Deleta pets
        supabase.from_("pets").delete().eq("proprietario_id", user_id).execute()

        # Deleta usuário
        supabase.from_("usuarios").delete().eq("id", user_id).execute()

        logger.info(f"✅ Conta deletada para usuário {user_id}")
        return True, "✅ Conta deletada com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao deletar conta: {e}")
        return False, f"❌ Erro: {e}"

def render():
    """Renderiza a página de conta do usuário."""
    st.header("👤 Minha Conta")

    # Verifica se usuário está logado
    usuario = st.session_state.get("usuario")
    if not usuario:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        st.stop()

    user_id = usuario.get("id")

    # Abas
    tab1, tab2, tab3 = st.tabs([
        "📋 Dados Pessoais",
        "🔐 Alterar Senha",
        "⚠️ Zona de Risco"
    ])

    # ABA 1: Dados Pessoais
    with tab1:
        st.subheader("📋 Dados Pessoais")

        col1, col2 = st.columns(2)

        with col1:
            novo_nome = st.text_input(
                "Nome",
                value=usuario.get("nome", ""),
                key="input_nome"
            )

        with col2:
            novo_email = st.text_input(
                "E-mail",
                value=usuario.get("email", ""),
                key="input_email"
            )

        if st.button("💾 Salvar Dados", key="btn_salvar_dados"):
            if not novo_nome or not novo_email:
                st.error("❌ Nome e e-mail são obrigatórios.")
            else:
                sucesso, mensagem = atualizar_dados_usuario(user_id, novo_nome, novo_email)
                if sucesso:
                    st.success(mensagem)
                    # Atualiza session_state
                    st.session_state.usuario["nome"] = novo_nome
                    st.session_state.usuario["email"] = novo_email
                    st.rerun()
                else:
                    st.error(mensagem)

        st.divider()

        # Informações da conta
        st.info(f"📅 **Tipo de Usuário:** {usuario.get('tipo_usuario', 'Tutor')}")
        st.info(f"✅ **E-mail Confirmado:** {'Sim' if usuario.get('email_confirmado') else 'Não'}")
        st.info(f"🕒 **Membro desde:** {usuario.get('criado_em', 'N/A')}")

    # ABA 2: Alterar Senha
    with tab2:
        st.subheader("🔐 Alterar Senha")

        senha_atual = st.text_input(
            "Senha Atual",
            type="password",
            key="input_senha_atual"
        )

        nova_senha = st.text_input(
            "Nova Senha",
            type="password",
            key="input_nova_senha",
            help="Mínimo 8 caracteres"
        )

        confirmar_senha = st.text_input(
            "Confirmar Nova Senha",
            type="password",
            key="input_confirmar_senha"
        )

        if st.button("🔄 Alterar Senha", key="btn_alterar_senha"):
            if not senha_atual or not nova_senha or not confirmar_senha:
                st.error("❌ Preencha todos os campos.")
            elif nova_senha != confirmar_senha:
                st.error("❌ As senhas não coincidem.")
            else:
                sucesso, mensagem = alterar_senha(user_id, senha_atual, nova_senha)
                if sucesso:
                    st.success(mensagem)
                    st.info("🔐 Faça login novamente com sua nova senha.")
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error(mensagem)

    # ABA 3: Zona de Risco
    with tab3:
        st.subheader("⚠️ Zona de Risco")
        st.warning("⚠️ As ações nesta seção são **irreversíveis**!")

        st.markdown("""
        ### 🗑️ Deletar Conta

        Ao deletar sua conta:
        - ❌ Todos os seus dados serão **permanentemente removidos**
        - ❌ Suas avaliações e pets serão **deletados**
        - ❌ Você não poderá recuperar essas informações
        """)

        if st.button("🗑️ Deletar Minha Conta", key="btn_deletar_conta"):
            st.warning("⚠️ Tem certeza? Esta ação é irreversível!")

            confirmacao = st.text_input(
                "Digite seu e-mail para confirmar:",
                key="input_confirmacao_email"
            )

            if confirmacao == usuario.get("email"):
                if st.button("✅ Confirmar Deleção", key="btn_confirmar_delecao"):
                    sucesso, mensagem = deletar_conta(user_id)
                    if sucesso:
                        st.success(mensagem)
                        st.info("Redirecionando para login...")
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.error(mensagem)
            elif confirmacao:
                st.error("❌ E-mail não corresponde.")

__all__ = ["render"]
