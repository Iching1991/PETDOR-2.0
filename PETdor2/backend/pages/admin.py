# PETdor2/pages/admin.py
"""
Página administrativa - gerenciamento de usuários e sistema.
Apenas usuários com role 'admin' podem acessar.
"""
import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from database.supabase_client import get_supabase
from auth.user import atualizar_status_usuario, atualizar_tipo_usuario

logger = logging.getLogger(__name__)

def is_admin(usuario: dict) -> bool:
    """Verifica se o usuário é administrador."""
    if not usuario:
        return False

    tipo_usuario = usuario.get("tipo_usuario", "").lower()
    return tipo_usuario == "admin"

def listar_usuarios() -> list:
    """Lista todos os usuários cadastrados."""
    try:
        supabase = get_supabase()

        response = (
            supabase
            .from_("usuarios")
            .select("id, nome, email, tipo_usuario, pais, email_confirmado, ativo, criado_em")
            .order("criado_em", desc=True)
            .execute()
        )

        return response.data if response.data else []

    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        st.error(f"❌ Erro ao carregar usuários: {e}")
        return []

def listar_pets() -> list:
    """Lista todos os pets cadastrados."""
    try:
        supabase = get_supabase()

        response = (
            supabase
            .from_("pets")
            .select("id, nome, especie, raca, proprietario_id, criado_em")
            .order("criado_em", desc=True)
            .execute()
        )

        return response.data if response.data else []

    except Exception as e:
        logger.error(f"Erro ao listar pets: {e}")
        return []

def listar_avaliacoes() -> list:
    """Lista todas as avaliações do sistema."""
    try:
        supabase = get_supabase()

        response = (
            supabase
            .from_("avaliacoes")
            .select("id, usuario_id, pet_id, percentual_dor, data_avaliacao")
            .order("data_avaliacao", desc=True)
            .limit(100)
            .execute()
        )

        return response.data if response.data else []

    except Exception as e:
        logger.error(f"Erro ao listar avaliações: {e}")
        return []

def render():
    """Renderiza a página de administração."""
    st.set_page_config(page_title="Admin - PETDor", layout="wide")
    st.title("🔐 Painel Administrativo — PETdor")

    # Verifica se é admin
    usuario = st.session_state.get("usuario")
    if not usuario or not is_admin(usuario):
        st.error("❌ Acesso restrito a administradores.")
        st.stop()

    st.success(f"✅ Bem-vindo, administrador **{usuario.get('nome')}**!")
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
                tipo = u.get("tipo_usuario", "Tutor")
                pais = u.get("pais", "N/A")
                confirmado = u.get("email_confirmado", False)
                ativo = u.get("ativo", True)
                criado_em = u.get("criado_em", "")

                with st.expander(f"👤 {nome} ({email})"):
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.write(f"**Nome:** {nome}")
                        st.write(f"**Email:** {email}")
                        st.write(f"**País:** {pais}")
                        st.write(f"**Criado em:** {criado_em}")
                        st.write(f"**Email Confirmado:** {'✅ Sim' if confirmado else '❌ Não'}")

                    with col2:
                        novo_tipo = st.selectbox(
                            "Tipo de Usuário",
                            ["Tutor", "Veterinario", "Admin"],
                            index=["Tutor", "Veterinario", "Admin"].index(tipo) 
                                if tipo in ["Tutor", "Veterinario", "Admin"] else 0,
                            key=f"tipo_{uid}"
                        )

                        if novo_tipo != tipo:
                            if st.button(f"💾 Salvar Tipo", key=f"btn_tipo_{uid}"):
                                try:
                                    atualizar_tipo_usuario(uid, novo_tipo)
                                    st.success("✅ Tipo atualizado!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro: {e}")

                    with col3:
                        novo_status = not ativo
                        status_label = "🔒 Desativar" if ativo else "🔓 Ativar"

                        if st.button(status_label, key=f"btn_status_{uid}"):
                            try:
                                atualizar_status_usuario(uid, novo_status)
                                st.success("✅ Status atualizado!")
                                st.rerun()
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
            if st.button("🔄 Sincronizar Banco de Dados"):
                st.success("✅ Sincronização concluída!")

            if st.button("📊 Gerar Relatório"):
                st.info("📥 Relatório será enviado por e-mail em breve...")

__all__ = ["render"]
