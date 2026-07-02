import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Painel de Dilatação", layout="wide")

# Configuração de Conexão
@st.cache_resource
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key("1A1SViUbrg8Kx9sH0bT2pKn9P59fcpWNHRDXeXiQQNIc")

def ler_dados():
    try:
        sh = get_connection()
        aba = sh.worksheet("Registros")
        data = aba.get_all_records()
        df = pd.DataFrame(data)
        # Garante que as colunas essenciais existam
        colunas_esperadas = ['PacienteID', 'QuantidadeGotas', 'Usuario']
        for col in colunas_esperadas:
            if col not in df.columns:
                df[col] = 0 if col == 'QuantidadeGotas' else ""
        return df, aba
    except:
        return pd.DataFrame(columns=['PacienteID', 'QuantidadeGotas', 'Usuario']), None

# Login
if 'usuario' not in st.session_state:
    st.sidebar.title("🔐 Login")
    user = st.sidebar.text_input("Seu Nome:")
    if st.sidebar.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

# Sidebar
with st.sidebar:
    st.title("💧 Painel")
    st.write(f"Operador: **{st.session_state.usuario}**")
    if st.button("🧹 Limpar Histórico"):
        sh = get_connection()
        aba = sh.worksheet("Registros")
        if aba.row_count > 1:
            aba.delete_rows(2, aba.row_count)
            st.rerun()

# Abas
tabs = st.tabs(["🏠 Dashboard", "💧 Aplicações", "📥 Importar"])
df, aba = ler_dados()

# 1. DASHBOARD
with tabs[0]:
    st.header("🏠 Monitoramento")
    if not df.empty:
        cols = st.columns(3)
        # Limpeza para evitar erros de tipo
        df['QuantidadeGotas'] = pd.to_numeric(df['QuantidadeGotas'], errors='coerce').fillna(0)
        for i, row in df.iterrows():
            with cols[i % 3]:
                gotas = int(row['QuantidadeGotas'])
                label = f"ID: {row['PacienteID']} | Gotas: {gotas}/10"
                if gotas <= 3: st.error("🔴 " + label)
                elif gotas <= 8: st.warning("🟡 " + label)
                else: st.success("🟢 " + label)
    else:
        st.info("Nenhum dado encontrado. Vá em 'Aplicações' ou 'Importar'.")

# 2. APLICAÇÕES
with tabs[1]:
    st.header("Registrar Gota")
    id_paciente = st.text_input("ID do Paciente para registrar 1 gota")
    if st.button("Confirmar Aplicação"):
        if id_paciente and aba:
            aba.append_row([id_paciente, 1, st.session_state.usuario])
            st.rerun()
    st.dataframe(df, use_container_width=True, hide_index=True)

# 3. IMPORTAR
with tabs[2]:
    st.header("📥 Importação")
    uploaded_file = st.file_uploader("CSV do HiperDoctor", type=["csv"])
    if uploaded_file and st.button("Processar"):
        df_import = pd.read_csv(uploaded_file)
        # Assegura que o nome do usuário logado vá para a coluna Usuario
        df_import['Usuario'] = st.session_state.usuario
        aba.append_rows(df_import.values.tolist())
        st.rerun()
