import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema Patrimonial Corporativo", layout="wide")

ARQUIVO_BASE = "equipamentos.csv"

# =============================
# USUÁRIOS
# =============================

USUARIOS = {
    "admin": {"senha": "admin123", "perfil": "admin", "regiao": None},
    "gestor_ne": {"senha": "1234", "perfil": "regional", "regiao": "Nordeste"},
}

# =============================
# FUNÇÕES
# =============================

def carregar_base():
    return pd.read_csv(ARQUIVO_BASE)

def salvar_base(df):
    df.to_csv(ARQUIVO_BASE, index=False)

# =============================
# LOGIN
# =============================

def login():
    st.title("🔐 Sistema Patrimonial Corporativo")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.session_state["perfil"] = USUARIOS[usuario]["perfil"]
            st.session_state["regiao"] = USUARIOS[usuario]["regiao"]
        else:
            st.error("Credenciais inválidas")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()
    st.stop()

# =============================
# CARREGAR BASE
# =============================

df = carregar_base()

if st.session_state["perfil"] == "regional":
    df = df[df["região"] == st.session_state["regiao"]]

# =============================
# SIDEBAR
# =============================

st.sidebar.success(st.session_state["usuario"])
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Cadastrar Equipamento",
    "Base Completa"
])

if st.sidebar.button("Sair"):
    st.session_state.clear()
    st.rerun()

# =============================
# DASHBOARD
# =============================

if menu == "Dashboard":

    st.title("📊 Dashboard Executivo")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Equipamentos", len(df))
    col2.metric("Regiões", df["região"].nunique())
    col3.metric("Categorias", df["categoria"].nunique())
    col4.metric("Ativos", df[df["status"] == "Ativo"].shape[0])

    st.markdown("### Distribuição por Categoria")
    st.bar_chart(df["categoria"].value_counts())

    st.markdown("### Distribuição por Região")
    st.bar_chart(df["região"].value_counts())

# =============================
# CADASTRAR
# =============================

elif menu == "Cadastrar Equipamento":

    st.title("➕ Cadastro de Equipamento")

    with st.form("cadastro"):
        regiao = st.text_input("Região")
        unidade = st.text_input("Unidade")
        categoria = st.text_input("Categoria")
        nome = st.text_input("Nome")
        serial = st.text_input("Serial")
        fabricante = st.text_input("Fabricante")
        modelo = st.text_input("Modelo")
        status = st.selectbox("Status", ["Ativo", "Manutenção", "Inativo", "Comodato"])
        data = st.date_input("Data Aquisição")
        obs = st.text_area("Observações")

        submitted = st.form_submit_button("Salvar")

        if submitted:
            novo = pd.DataFrame([{
                "região": regiao,
                "unidade": unidade,
                "categoria": categoria,
                "nome": nome,
                "serial": serial,
                "fabricante": fabricante,
                "modelo": modelo,
                "status": status,
                "data_aquisicao": data,
                "observacoes": obs
            }])

            base_atual = carregar_base()
            base_atual = pd.concat([base_atual, novo], ignore_index=True)
            salvar_base(base_atual)

            st.success("Equipamento cadastrado com sucesso!")

# =============================
# BASE COMPLETA
# =============================

elif menu == "Base Completa":

    st.title("📋 Base Patrimonial")

    busca = st.text_input("Buscar equipamento")

    df_filtrado = df.copy()

    if busca:
        df_filtrado = df_filtrado[
            df_filtrado.apply(lambda row: busca.lower() in str(row).lower(), axis=1)
        ]

    st.dataframe(df_filtrado, use_container_width=True)

    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Exportar CSV", csv, "base_patrimonial.csv")
