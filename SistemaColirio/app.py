import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Gestão de Dilatação", layout="wide")

@st.cache_resource
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key("1A1SViUbrg8Kx9sH0bT2pKn9P59fcpWNHRDXeXiQQNIc")

def ler_dados():
    sh = get_connection()
    aba = sh.worksheet("Registros")
    data = aba.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty and 'QuantidadeGotas' in df.columns:
        df['QuantidadeGotas'] = pd.to_numeric(df['QuantidadeGotas'], errors='coerce').fillna(0).astype(int)
    return df, aba

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
        for i, row in df.iterrows():
            with cols[i % 3]:
                # Usa .get para evitar erro se a coluna não existir
                gotas = int(pd.to_numeric(row.get('QuantidadeGotas', 0), errors='coerce'))
                label = f"ID: {row.get('PacienteID', 'N/A')} | Gotas: {gotas}/10"
                if gotas <= 3: st.error("🔴 " + label)
                elif gotas <= 8: st.warning("🟡 " + label)
                else: st.success("🟢 " + label)

# 2. APLICAÇÕES
with tabs[1]:
    st.header("Registrar Gota")
    id_paciente = st.text_input("ID do Paciente:")
    if st.button("Confirmar Aplicação"):
        if id_paciente:
            # Insere dados básicos
            aba.append_row([id_paciente, "N/A", 1, st.session_state.usuario])
            st.rerun()
    st.dataframe(df, use_container_width=True, hide_index=True)

# 3. IMPORTAR (BLINDADO)
with tabs[2]:
    st.header("📥 Importação")
    uploaded_file = st.file_uploader("CSV do HiperDoctor", type=["csv"])
    if uploaded_file is not None:
        if st.button("Processar Importação"):
            df_import = pd.read_csv(uploaded_file)
            
            # CRIAÇÃO AUTOMÁTICA DE COLUNAS FALTANTES
            colunas_necessarias = ['PacienteID', 'NomePaciente', 'QuantidadeGotas', 'Usuario']
            for col in colunas_necessarias:
                if col not in df_import.columns:
                    df_import[col] = "" # Cria a coluna vazia se ela não existir no CSV
            
            # Força o nome do usuário logado na coluna 'Usuario'
            df_import['Usuario'] = st.session_state.usuario
            
            # Seleciona apenas as colunas certas e na ordem correta
            df_final = df_import[colunas_necessarias]
            
            # Envia para a planilha
            aba.append_rows(df_final.values.tolist())
            st.success("Dados importados com sucesso!")
            st.rerun()
