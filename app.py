import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Gestão de Equipamentos",
    page_icon="🏢",
    layout="wide"
)

# -------------------------
# BASE DE USUÁRIOS
# -------------------------

USUARIOS = {
    "admin": {
        "senha": "admin123",
        "perfil": "admin",
        "regiao": None
    },
    "nordeste": {
        "senha": "1234",
        "perfil": "regional",
        "regiao": "Nordeste"
    }
}

# -------------------------
# LOGIN
# -------------------------

def tela_login():
    st.markdown("## 🔐 Acesso à Plataforma")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.session_state["perfil"] = USUARIOS[usuario]["perfil"]
            st.session_state["regiao"] = USUARIOS[usuario]["regiao"]
        else:
            st.error("Usuário ou senha inválidos")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    tela_login()
    st.stop()

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.success(f"👤 {st.session_state['usuario']}")
st.sidebar.write(f"Perfil: {st.session_state['perfil']}")

if st.sidebar.button("Sair"):
    st.session_state.clear()
    st.rerun()

# -------------------------
# TÍTULO
# -------------------------

st.title("📊 Plataforma Corporativa de Equipamentos")
st.markdown("---")

# -------------------------
# UPLOAD
# -------------------------

uploaded_file = st.file_uploader(
    "Envie a planilha de equipamentos",
    type=["xlsx", "csv"]
)

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.lower().str.strip()

    # FILTRO POR PERFIL
    if st.session_state["perfil"] == "regional":
        if "região" in df.columns:
            df = df[df["região"] == st.session_state["regiao"]]

    # DASHBOARD EXECUTIVO
    col1, col2, col3 = st.columns(3)

    col1.metric("Total de Equipamentos", len(df))

    if "região" in df.columns:
        col2.metric("Total de Regiões", df["região"].nunique())

    if "categoria" in df.columns:
        col3.metric("Categorias", df["categoria"].nunique())

    st.markdown("---")

    # FILTROS
    filtro1, filtro2, filtro3 = st.columns(3)

    if "região" in df.columns:
        with filtro1:
            regiao = st.multiselect("Região", df["região"].unique())
    else:
        regiao = []

    if "unidade" in df.columns:
        with filtro2:
            unidade = st.multiselect("Unidade", df["unidade"].unique())
    else:
        unidade = []

    if "categoria" in df.columns:
        with filtro3:
            categoria = st.multiselect("Categoria", df["categoria"].unique())
    else:
        categoria = []

    busca_serial = st.text_input("🔎 Buscar por Número de Série")

    df_filtrado = df.copy()

    if regiao:
        df_filtrado = df_filtrado[df_filtrado["região"].isin(regiao)]

    if unidade:
        df_filtrado = df_filtrado[df_filtrado["unidade"].isin(unidade)]

    if categoria:
        df_filtrado = df_filtrado[df_filtrado["categoria"].isin(categoria)]

    if busca_serial and "serial" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado["serial"].astype(str).str.contains(busca_serial, case=False)
        ]

    st.markdown("### 📋 Lista de Equipamentos")
    st.dataframe(df_filtrado, use_container_width=True)

    # GRÁFICOS
    if "categoria" in df.columns:
        st.markdown("### 📈 Distribuição por Categoria")
        st.bar_chart(df_filtrado["categoria"].value_counts())

else:
    st.info("Aguardando upload da planilha.")
