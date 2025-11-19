"""
streamlit_app.py
Entrada principal do PETDor2.0 para Streamlit Cloud (ou local).
- Inicializa banco e migrações
- Fornece menu lateral com fluxo: Login / Cadastro / Cadastrar Pet / Avaliar / Histórico / Conta / Admin / Sair
- Integra com: database.*, auth.*, especies.*, utils.*
"""

import os
from datetime import datetime
import streamlit as st

# Inicialização e imports locais (projeto organizado)
try:
    from database.migration import criar_tabelas, migrar_banco_completo
    from database.connection import conectar_db
    from auth.user import cadastrar_usuario, autenticar_usuario, buscar_usuario_por_id
    from database.models import buscar_usuario_por_email, buscar_pet_por_id  # optional
    from especies import get_especies_nomes, get_especie_config
    from utils.pdf_generator import gerar_pdf_relatorio
    from utils.email_sender import enviar_email
except Exception as e:
    st.error("Erro ao importar módulos internos do projeto. Verifique a estrutura das pastas.")
    st.exception(e)
    raise

# --------- App config ----------
APP_TITLE = "🐾 PETDor2.0"
st.set_page_config(page_title=APP_TITLE, page_icon="🐾", layout="wide", initial_sidebar_state="auto")

# --------- Inicializar DB / Migrações (seguro para múltiplas execuções) ----------
with st.spinner("Inicializando banco e aplicando migrações..."):
    try:
        # funções idempotentes para criar tabelas
        criar_tabelas()
    except Exception as exc:
        st.error("Falha ao criar tabelas do banco.")
        st.exception(exc)

# --------- Utilitários de sessão ----------
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

def require_login():
    if not st.session_state.get("user_id"):
        st.warning("Você precisa estar logado para acessar esta página.")
        st.stop()

# --------- UI: Sidebar (navegação) ----------
st.sidebar.markdown(f"## {APP_TITLE}")
if st.session_state.get("user_name"):
    st.sidebar.success(f"👋 {st.session_state['user_name']}")

menu = st.sidebar.radio(
    "Navegação",
    ["Home", "Login", "Criar Conta", "Cadastrar Pet", "Avaliar", "Histórico", "Conta", "Admin"],
    index=0
)

# logout
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.experimental_rerun()

# --------- Home ----------
def page_home():
    st.markdown(f"# {APP_TITLE}")
    st.markdown("Sistema profissional de avaliação de dor em animais de companhia.")
    st.markdown("---")

    st.markdown(
        """
        **Recursos principais**
        - Avaliações padronizadas por espécie (cães, gatos, coelhos, porquinhos-da-índia, aves, répteis).
        - Histórico completo, exportação e geração de relatórios em PDF.
        - Contas para Tutores, Clínicas e Veterinários.
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avaliações realizadas (teste)", "—")
    with col2:
        st.metric("Pets cadastrados", "—")

# --------- Login ----------
def page_login():
    st.header("🔐 Login")
    email = st.text_input("E-mail", key="login_email")
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar"):
        ok, msg, user_id = autenticar_usuario(email, senha)
        if ok:
            st.success(msg)
            st.session_state["user_id"] = user_id
            # obter nome
            user = buscar_usuario_por_id(user_id)
            st.session_state["user_name"] = user.get("nome") if user else None
            st.experimental_rerun()
        else:
            st.error(msg)

    st.markdown("---")
    st.write("Se você não tem conta, use 'Criar Conta' no menu lateral.")

# --------- Criar Conta ----------
def page_criar_conta():
    st.header("📝 Criar Conta")
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    tipo = st.selectbox("Tipo de usuário", ["Tutor", "Veterinario", "Clinica"])
    pais = st.text_input("País", value="Brasil")

    if st.button("Criar conta"):
        ok, msg = cadastrar_usuario(nome, email, senha, confirmar, tipo, pais)
        if ok:
            st.success(msg)
            st.info("Cheque seu e-mail para confirmar (simulação). Faça login em seguida.")
        else:
            st.error(msg)

# --------- Cadastrar Pet ----------
def page_cadastrar_pet():
    require_login()
    st.header("🟢 Cadastrar Pet")
    conn = conectar_db()
    cur = conn.cursor()

    # carrega espécies disponíveis
    especies = get_especies_nomes()
    if not especies:
        st.error("Nenhuma espécie cadastrada no sistema.")
        return

    nome = st.text_input("Nome do Pet")
    especie = st.selectbox("Espécie", especies)
    raca = st.text_input("Raça (opcional)")
    peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
    foto = st.file_uploader("Foto do pet (opcional)", type=["png","jpg","jpeg"])

    if st.button("Salvar Pet"):
        if not nome:
            st.error("Nome do pet é obrigatório.")
        else:
            try:
                cur.execute(
                    "INSERT INTO pets (tutor_id, nome, especie, raca, peso, data_cadastro) VALUES (?, ?, ?, ?, ?, ?)",
                    (st.session_state["user_id"], nome, especie, raca or None, float(peso) if peso else None, datetime.now().isoformat())
                )
                conn.commit()
                st.success("Pet cadastrado com sucesso.")
            except Exception as e:
                st.error("Erro ao cadastrar pet.")
                st.exception(e)
    conn.close()

# --------- Avaliar ----------
def page_avaliar():
    require_login()
    st.header("📋 Avaliar Pet")
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, especie FROM pets WHERE tutor_id = ?", (st.session_state["user_id"],))
    pets = cur.fetchall()
    if not pets:
        st.info("Você não tem pets cadastrados. Cadastre um primeiro.")
        conn.close()
        return

    pet_map = {f"{r['nome']} — {r['especie']} (#{r['id']})": r for r in pets}
    escolha = st.selectbox("Escolha o pet", list(pet_map.keys()))
    pet = pet_map[escolha]

    # carregar configuração de espécie
    config = get_especie_config(pet["especie"])
    if not config:
        st.error("Configuração da espécie não encontrada.")
        conn.close()
        return

    st.subheader(f"{pet['nome']} — {config.nome}")
    st.write(config.descricao)
    observacoes = st.text_area("Observações (opcional)")

    # perguntas dinamicas
    st.markdown("**Responda as perguntas (0 = nunca / 7 = sempre)**")
    respostas = {}
    max_possivel = sum(p.peso * 7 for p in config.perguntas) or 1

    for idx, p in enumerate(config.perguntas, start=1):
        key = f"q_{pet['id']}_{idx}"
        val = st.slider(p.texto, 0, 7, 0, key=key)
        respostas[f"q_{idx}"] = {"valor": val, "invertida": p.invertida, "peso": p.peso, "texto": p.texto}

    if st.button("Calcular e Salvar Avaliação"):
        soma = 0.0
        for info in respostas.values():
            v = int(info["valor"])
            if info["invertida"]:
                v = 7 - v
            soma += v * float(info["peso"])
        percentual = round((soma / max_possivel) * 100, 1)

        # salva avaliação
        try:
            # garantir tabela avaliacao_respostas (migration pode ter criado, mas reforçamos)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS avaliacao_respostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    avaliacao_id INTEGER NOT NULL,
                    pergunta_id TEXT NOT NULL,
                    resposta INTEGER NOT NULL
                )
            """)
            cur.execute(
                "INSERT INTO avaliacoes (pet_id, usuario_id, percentual_dor, observacoes, data_avaliacao) VALUES (?, ?, ?, ?, ?)",
                (pet["id"], st.session_state["user_id"], percentual, observacoes, datetime.now().isoformat())
            )
            aid = cur.lastrowid
            for pid, info in respostas.items():
                cur.execute("INSERT INTO avaliacao_respostas (avaliacao_id, pergunta_id, resposta) VALUES (?, ?, ?)",
                            (aid, pid, int(info["valor"])))
            conn.commit()
            st.success(f"Avaliação salva (ID: {aid}) — Dor: {percentual}%")
            # gerar PDF
            pdf_path = gerar_pdf_relatorio(pet["nome"], {
                "percentual": percentual,
                "observacoes": observacoes,
                "respostas": {k: v["valor"] for k, v in respostas.items()},
                "data": datetime.now().isoformat()
            })
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Baixar PDF", f, file_name=os.path.basename(pdf_path))
        except Exception as e:
            st.error("Erro ao salvar avaliação.")
            st.exception(e)

    conn.close()

# --------- Histórico ----------
def page_historico():
    require_login()
    st.header("📊 Histórico de Avaliações")
    conn = conectar_db(); cur = conn.cursor()
    # filtrar por pet
    cur.execute("SELECT id, nome FROM pets WHERE tutor_id = ?", (st.session_state["user_id"],))
    pets = cur.fetchall()
    pet_options = ["Todos"] + [f"{r['nome']} (#{r['id']})" for r in pets]
    escolha = st.selectbox("Filtrar por pet", pet_options)

    query = """
        SELECT a.id, a.pet_id, a.percentual_dor, a.observacoes, a.data_avaliacao, p.nome as pet_nome
        FROM avaliacoes a
        JOIN pets p ON a.pet_id = p.id
        WHERE a.usuario_id = ?
    """
    params = [st.session_state["user_id"]]
    if escolha != "Todos":
        pid = int(escolha.split("(#")[-1].rstrip(")"))
        query += " AND a.pet_id = ?"
        params.append(pid)
    query += " ORDER BY a.data_avaliacao DESC LIMIT 200"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()

    if not rows:
        st.info("Nenhuma avaliação encontrada.")
        conn.close()
        return

    # tabela simples
    data = []
    for r in rows:
        data.append({
            "ID": r["id"],
            "Pet": r["pet_nome"],
            "Dor (%)": r["percentual_dor"],
            "Data": r["data_avaliacao"],
            "Observações": r["observacoes"] or ""
        })
    st.table(data)

    # seleção para ver detalhes
    sel = st.selectbox("Ver avaliação (ID)", [r["id"] for r in rows])
    cur.execute("SELECT * FROM avaliacoes WHERE id = ?", (sel,))
    aval = cur.fetchone()
    if aval:
        st.markdown(f"**Avaliação #{aval['id']} — Pet ID {aval['pet_id']}**")
        st.write(f"Percentual: {aval['percentual_dor']}%")
        st.write(f"Data: {aval['data_avaliacao']}")
        st.write(f"Observações: {aval['observacoes']}")
        # respostas
        cur.execute("SELECT pergunta_id, resposta FROM avaliacao_respostas WHERE avaliacao_id = ? ORDER BY id", (aval["id"],))
        resp = cur.fetchall()
        if resp:
            for r in resp:
                st.write(f"- {r['pergunta_id']}: {r['resposta']}")

    conn.close()

# --------- Conta ----------
def page_conta():
    require_login()
    st.header("👤 Minha Conta")
    user = buscar_usuario_por_id(st.session_state["user_id"])
    if not user:
        st.error("Usuário não encontrado.")
        return

    st.write(f"**Nome:** {user['nome']}")
    st.write(f"**E-mail:** {user['email']}")
    st.write(f"**Tipo:** {user.get('tipo_usuario', 'Tutor')}")
    st.write(f"**País:** {user.get('pais', '—')}")

# --------- Admin (simples) ----------
def page_admin():
    require_login()
    user = buscar_usuario_por_id(st.session_state["user_id"])
    if not user or user.get("tipo_usuario", "").lower() != "clinica" and user.get("tipo_usuario", "").lower() != "veterinario":
        st.error("Acesso restrito: somente administradores ou profissionais.")
        return
    st.header("🔐 Administração")
    st.info("Painel administrativo (em desenvolvimento).")

# --------- Roteador ----------
PAGES = {
    "Home": page_home,
    "Login": page_login,
    "Criar Conta": page_criar_conta,
    "Cadastrar Pet": page_cadastrar_pet,
    "Avaliar": page_avaliar,
    "Histórico": page_historico,
    "Conta": page_conta,
    "Admin": page_admin
}

# executa página selecionada
page_func = PAGES.get(menu, page_home)
page_func()
