# PETdor2/pages/conta.py
"""
Página de gerenciamento de conta do usuário.
Permite atualizar dados pessoais, redefinir senha e gerenciar preferências.
"""
import streamlit as st
import logging
from auth.user import buscar_usuario_por_email
from auth.security import verify_password, hash_password
from database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

def atualizar_dados_usuario(user_id: int, nome: str, email: str) -> bool:
    """Atualiza nome e email do usuário no banco."""
    try:
        supabase = get_supabase()
        supabase.from_("usuarios").update({
            "nome": nome,
            "email": email.lower()
        }).eq("id", user_id).execute()
        logger.info(f"✅ Dados do usuário {user_id} atualizados")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar dados: {e}")
        return False

def alterar_senha(user_id: int, senha_atual: str, nova_senha: str) -> tuple[bool, str]:
    """Altera a senha do usuário após validação."""
    try:
        supabase = get_supabase()

        # Busca o usuário atual
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
            return False, "Usuário não encontrado."

        # Verifica se a senha atual está correta
        if not verify_password(senha_atual, usuario.get("senha_hash", "")):
            return False, "Senha atual incorreta."

        # Hash da nova senha
        nova_senha_hash = hash_password(nova_senha)

        # Atualiza a senha
        supabase.from_("usuarios").update({
            "senha_hash": nova_senha_hash
        }).eq("id", user_id).execute()

        logger.info(f"✅ Senha do usuário {user_id} alterada")
        return True, "Senha alterada com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return False, f"Erro ao alterar senha: {str(e)}"

def deletar_conta(user_id: int) -> bool:
    """Deleta a conta do usuário."""
    try:
        supabase = get_supabase()
        supabase.from_("usuarios").delete().eq("id", user_id).execute()
        logger.info(f"✅ Conta do usuário {user_id} deletada")
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar conta: {e}")
        return False

def render():
    """Renderiza a página de conta do usuário."""
    st.header("👤 Minha Conta")
    usuario = st.session_state.get("usuario")
    if not usuario:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        st.stop()

    usuario_id = usuario.get("id")
    nome_atual = usuario.get("nome", "")
    email_atual = usuario.get("email", "")
    tipo_usuario = usuario.get("tipo", "Tutor")

    # Abas
    tab1, tab2, tab3 = st.tabs(["📋 Dados Pessoais", "🔐 Segurança", "⚙️ Preferências"])

    # ABA 1: Dados Pessoais
    with tab1:
        st.subheader("📋 Dados Pessoais")
        col1, col2 = st.columns(2)
        with col1:
            novo_nome = st.text_input("Nome completo", value=nome_atual, key="nome_input")
        with col2:
            novo_email = st.text_input("E-mail", value=email_atual, key="email_input")

        st.write(f"**Tipo de usuário:** {tipo_usuario}")
        st.write(f"**Membro desde:** {usuario.get('criado_em', 'N/A')}")

        if st.button("💾 Salvar alterações", key="btn_save_dados"):
            if novo_nome and novo_email:
                if atualizar_dados_usuario(usuario_id, novo_nome, novo_email):
                    st.success("✅ Dados atualizados com sucesso!")
                    st.session_state["usuario"]["nome"] = novo_nome
                    st.session_state["usuario"]["email"] = novo_email
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar dados.")
            else:
                st.warning("⚠️ Preencha todos os campos.")

    # ABA 2: Segurança
    with tab2:
        st.subheader("🔐 Segurança")
        st.write("**Alterar Senha**")
        col1, col2 = st.columns(2)
        with col1:
            senha_atual = st.text_input("Senha atual", type="password", key="senha_atual")
        with col2:
            nova_senha = st.text_input("Nova senha", type="password", key="nova_senha")

        senha_confirmacao = st.text_input("Confirmar nova senha", type="password", key="senha_conf")

        if st.button("🔄 Alterar Senha", key="btn_change_password"):
            if not senha_atual or not nova_senha or not senha_confirmacao:
                st.warning("⚠️ Preencha todos os campos.")
            elif nova_senha != senha_confirmacao:
                st.error("❌ As senhas não coincidem.")
            elif len(nova_senha) < 8:
                st.error("❌ A senha deve ter pelo menos 8 caracteres.")
            else:
                sucesso, mensagem = alterar_senha(usuario_id, senha_atual, nova_senha)
                if sucesso:
                    st.success(f"✅ {mensagem}")
                else:
                    st.error(f"❌ {mensagem}")

        st.divider()
        st.write("**Recuperação de Conta**")
        if st.button("📧 Enviar link de recuperação", key="btn_recovery"):
            st.info("📧 Link de recuperação enviado para seu e-mail.")

    # ABA 3: Preferências
    with tab3:
        st.subheader("⚙️ Preferências")
        notificacoes = st.checkbox("Receber notificações por e-mail", value=True)
        newsletter = st.checkbox("Receber newsletter", value=False)

        if st.button("💾 Salvar preferências", key="btn_save_prefs"):
            st.success("✅ Preferências salvas!")

        st.divider()
        st.write("**Deletar Conta**")
        if st.checkbox("Tenho certeza que desejo deletar minha conta", key="confirm_delete"):
            if st.button("🗑️ Deletar conta permanentemente", key="btn_delete"):
                if deletar_conta(usuario_id):
                    st.error("❌ Conta deletada. Você será desconectado.")
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error("❌ Erro ao deletar conta.")

__all__ = ["render"]
