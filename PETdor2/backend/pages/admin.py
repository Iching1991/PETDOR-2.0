# PetDor2/backend/pages/admin.py
"""
Página administrativa - gerenciamento de usuários e sistema.
Apenas usuários com role 'admin' podem acessar.
"""
import streamlit as st
import pandas as pd
import logging
from datetime import datetime

# ============================================================
# 🔧 CORREÇÃO DOS IMPORTS (ABSOLUTOS a partir de 'backend')
# ============================================================
# Importa as funções de acesso ao Supabase diretamente do pacote 'database'
from backend.database import supabase_table_select, supabase_table_update
# Importa as funções de atualização de usuário do pacote 'auth.user'
from backend.auth.user import atualizar_status_usuario, atualizar_usuario # Usaremos atualizar_usuario para o tipo

logger = logging.getLogger(__name__)

# ============================================================
# Funções de Acesso a Dados (usando supabase_table_select/update)
# ============================================================

def is_admin(user_data: dict) -> bool:
    """Verifica se o usuário é administrador com base nos dados da sessão."""
    if not user_data:
        return False
    # A coluna 'is_admin' é um booleano no Supabase
    return user_data.get("is_admin", False)

def listar_usuarios() -> list:
    """Lista todos os usuários cadastrados usando supabase_table_select."""
    try:
        ok, usuarios = supabase_table_select(
            "usuarios",
            "id, nome, email, tipo, pais, email_confirmado, ativo, is_admin, criado_em", # Ajustado para 'tipo' e 'is_admin'
            order_by="criado_em",
            desc=True,
            single=False
        )
        if ok:
            return usuarios if usuarios else []
        else:
            logger.error(f"Erro ao listar usuários: {usuarios}")
            st.error(f"❌ Erro ao carregar usuários: {usuarios}")
            return []
    except Exception as e:
        logger.exception("Erro inesperado ao listar usuários")
        st.error(f"❌ Erro inesperado ao carregar usuários: {e}")
        return []

def listar_pets() -> list:
    """Lista todos os pets cadastrados usando supabase_table_select."""
    try:
        ok, pets = supabase_table_select(
            "pets",
            "id, nome, especie, raca, proprietario_id, criado_em",
            order_by="criado_em",
            desc=True,
            single=False
        )
        if ok:
            return pets if pets else []
        else:
            logger.error(f"Erro ao listar pets: {pets}")
            st.error(f"❌ Erro ao carregar pets: {pets}")
            return []
    except Exception as e:
        logger.exception("Erro inesperado ao listar pets")
        st.error(f"❌ Erro inesperado ao carregar pets: {e}")
        return []

def listar_avaliacoes() -> list:
    """Lista todas as avaliações do sistema usando supabase_table_select."""
    try:
        ok, avaliacoes = supabase_table_select(
            "avaliacoes",
            "id, usuario_id, pet_id, percentual_dor, data_avaliacao",
            order_by="data_avaliacao",
            desc=True,
            limit=100,
            single=False
        )
        if ok:
            return avaliacoes if avaliacoes else []
        else:
            logger.error(f"Erro ao listar avaliações: {avaliacoes}")
            st.error(f"❌ Erro ao carregar avaliações: {avaliacoes}")
            return []
    except Exception as e:
        logger.exception("Erro inesperado ao listar avaliações")
        st.error(f"❌ Erro inesperado ao carregar avaliações: {e}")
        return []

# ============================================================
# Renderização da Página
# ============================================================

def render(user_data: dict = None):
    """Renderiza a página de administração."""
    # st.set_page_config(page_title="Admin - PETDor", layout="wide") # Não deve ser chamado dentro de uma função render
    st.title("🔐 Painel Administrativo — PETdor")

    # Verifica se é admin
    # O user_data já vem do st.session_state.user_data passado pelo streamlit_app.py
    if not user_data or not is_admin(user_data):
        st.error("❌ Acesso restrito a administradores.")
        st.stop() # Interrompe a execução da página para não mostrar conteúdo restrito

    st.success(f"✅ Bem-vindo, administrador **{user_data.get('nome', 'Usuário')}**!")
    st.divider()

    # Menu de abas
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Usuários",
        "🐾 Pets",
        "📊 Avaliações",
        "⚙️ Configurações"
    ])

    # ABA 1: Usuários
    with tab1:
        st.subheader("👥 Gerenciamento de Usuários")
        usuarios = listar_usuarios()
        if not usuarios:
            st.info("📭 Nenhum usuário cadastrado.")
        else:
            st.metric("Total de Usuários", len(usuarios))
            st.divider()
            # Exibir usuários em cards
            for u in usuarios:
                uid = u.get("id")
                nome = u.get("nome", "Desconhecido")
                email = u.get("email", "")
                tipo_atual = u.get("tipo", "Tutor") # Ajustado para 'tipo'
                pais = u.get("pais", "N/A")
                confirmado = u.get("email_confirmado", False)
                ativo = u.get("ativo", True)
                is_admin_user = u.get("is_admin", False) # Pega o status de admin do usuário
                criado_em = u.get("criado_em", "")

                with st.expander(f"👤 {nome} ({email})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Nome:** {nome}")
                        st.write(f"**Email:** {email}")
                        st.write(f"**País:** {pais}")
                        st.write(f"**Criado em:** {criado_em}")
                        st.write(f"**Email Confirmado:** {'✅ Sim' if confirmado else '❌ Não'}")
                        st.write(f"**É Administrador:** {'👑 Sim' if is_admin_user else 'No'}") # Exibe status de admin
                    with col2:
                        # Opções de tipo de usuário
                        opcoes_tipo = ["Tutor", "Veterinario", "Admin"]
                        # Garante que o tipo atual esteja nas opções, senão usa "Tutor" como padrão
                        index_tipo = opcoes_tipo.index(tipo_atual) if tipo_atual in opcoes_tipo else 0
                        novo_tipo = st.selectbox(
                            "Tipo de Usuário",
                            opcoes_tipo,
                            index=index_tipo,
                            key=f"tipo_{uid}"
                        )
                        # Opção para definir/remover como Admin (booleano)
                        novo_is_admin = st.checkbox(
                            "Tornar Admin",
                            value=is_admin_user,
                            key=f"is_admin_{uid}"
                        )

                        # Botão para salvar tipo e status de admin
                        if st.button(f"💾 Salvar Tipo/Admin", key=f"btn_tipo_admin_{uid}"):
                            try:
                                # Chama atualizar_usuario para tipo e is_admin
                                sucesso, msg = atualizar_usuario(uid, tipo=novo_tipo, is_admin=novo_is_admin)
                                if sucesso:
                                    st.success("✅ Tipo e status de Admin atualizados!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao atualizar: {msg}")
                            except Exception as e:
                                st.error(f"❌ Erro: {e}")

                    with col3:
                        novo_status = not ativo
                        status_label = "🔒 Desativar" if ativo else "🔓 Ativar"
                        if st.button(status_label, key=f"btn_status_{uid}"):
                            try:
                                # Chama atualizar_status_usuario
                                sucesso, msg = atualizar_status_usuario(uid, novo_status)
                                if sucesso:
                                    st.success("✅ Status atualizado!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao atualizar status: {msg}")
                            except Exception as e:
                                st.error(f"❌ Erro: {e}")
                    st.divider()

    # ABA 2: Pets
    with tab2:
        st.subheader("🐾 Gerenciamento de Pets")
        pets = listar_pets()
        if not pets:
            st.info("📭 Nenhum pet cadastrado.")
        else:
            df_pets = pd.DataFrame(pets)
            st.metric("Total de Pets", len(pets))
            st.divider()
            st.dataframe(df_pets, use_container_width=True)

    # ABA 3: Avaliações
    with tab3:
        st.subheader("📊 Histórico de Avaliações")
        avaliacoes = listar_avaliacoes()
        if not avaliacoes:
            st.info("📭 Nenhuma avaliação registrada.")
        else:
            df_avaliacoes = pd.DataFrame(avaliacoes)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Avaliações", len(avaliacoes))
            with col2:
                dor_media = df_avaliacoes["percentual_dor"].mean()
                st.metric("Dor Média", f"{dor_media:.1f}%")
            with col3:
                dor_maxima = df_avaliacoes["percentual_dor"].max()
                st.metric("Dor Máxima", f"{dor_maxima}%")
            st.divider()
            st.dataframe(df_avaliacoes, use_container_width=True)

    # ABA 4: Configurações
    with tab4:
        st.subheader("⚙️ Configurações do Sistema")
        col1, col2 = st.columns(2)
        with col1:
            st.info("ℹ️ **Versão:** PETDor 2.0")
            st.info("📅 **Acesso:** " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        with col2:
            # Ações de sincronização e relatório são placeholders, pois não temos a implementação
            if st.button("🔄 Sincronizar Banco de Dados"):
                st.success("✅ Sincronização concluída!")
            if st.button("📊 Gerar Relatório"):
                st.info("📥 Relatório será enviado por e-mail em breve...")

__all__ = ["render"]
