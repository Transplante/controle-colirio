import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestão de Dilatação", layout="wide")

# Conexão com Google Sheets
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
    # Garante que a coluna de gotas seja numérica
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
                gotas = int(row['QuantidadeGotas'])
                label = f"ID: {row.get('PacienteID', 'N/A')} | Gotas: {gotas}/10"
                if gotas <= 3: st.error("🔴 " + label)
                elif gotas <= 8: st.warning("🟡 " + label)
                else: st.success("🟢 " + label)
    else:
        st.info("Nenhum dado encontrado.")

# 2. APLICAÇÕES
with tabs[1]:
    st.header("Registrar Gota")
    id_paciente = st.text_input("ID do Paciente:")
    if st.button("Confirmar Aplicação"):
        if id_paciente:
            # Insere: ID, Nome Vazio (ou padrão), Quantidade (1), Usuário Logado
            aba.append_row([id_paciente, "N/A", 1, st.session_state.usuario])
            st.rerun()
    st.dataframe(df, use_container_width=True, hide_index=True)

# 3. IMPORTAR
with tabs[2]:
    st.header("📥 Importação")
    uploaded_file = st.file_uploader("CSV do HiperDoctor", type=["csv"])
    if uploaded_file is not None:
        if st.button("Processar Importação"):
            df_import = pd.read_csv(uploaded_file)
            
            # Força o nome do usuário logado na coluna 'Usuario'
            df_import['Usuario'] = st.session_state.usuario
            
            # Garante que as colunas do CSV coincidam com a ordem da planilha
            # Supondo colunas: PacienteID, NomePaciente, QuantidadeGotas, Usuario
            df_final = df_import[['PacienteID', 'NomePaciente', 'QuantidadeGotas', 'Usuario']]
            
            aba.append_rows(df_final.values.tolist())
            st.success("Dados importados com seu nome de operador!")
            st.rerun()
