import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Painel de Dilatação Pro", layout="wide")

# Conexão
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
    # LIMPEZA CRÍTICA: Transforma a coluna de gotas em números, ignorando erros
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
    st.title("💧 Painel de Dilatação")
    st.write(f"Operador: **{st.session_state.usuario}**")
    st.divider()
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
    st.header("🏠 Monitoramento de Pacientes")
    if not df.empty:
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                gotas = int(row['QuantidadeGotas'])
                # Lógica: 1-3 Vermelho, 4-8 Amarelo, 9+ Verde
                if gotas <= 3:
                    st.error(f"🔴 **{row.get('NomePaciente', 'N/A')}**\n\nID: {row.get('PacienteID', 'N/A')}\nGotas: {gotas}/10\nResp: {row.get('Usuario', 'N/A')}")
                elif 4 <= gotas <= 8:
                    st.warning(f"🟡 **{row.get('NomePaciente', 'N/A')}**\n\nID: {row.get('PacienteID', 'N/A')}\nGotas: {gotas}/10\nResp: {row.get('Usuario', 'N/A')}")
                else:
                    st.success(f"🟢 **{row.get('NomePaciente', 'N/A')}**\n\nID: {row.get('PacienteID', 'N/A')}\nGotas: {gotas}/10\nResp: {row.get('Usuario', 'N/A')}")
    else:
        st.info("Nenhum paciente registrado.")

# 2. APLICAÇÕES
with tabs[1]:
    st.header("Registrar Aplicação")
    paciente_id = st.text_input("ID do Paciente")
    nome_paciente = st.text_input("Nome do Paciente")
    if st.button("Confirmar Gota"):
        # Adiciona 1 gota (pode ser ajustado)
        aba.append_row([paciente_id, nome_paciente, 1, st.session_state.usuario])
        st.rerun()
    st.dataframe(df)

# 3. IMPORTAR
with tabs[2]:
    st.header("📥 Importação HiperDoctor")
    uploaded_file = st.file_uploader("CSV do HiperDoctor", type=["csv"])
    if uploaded_file and st.button("Confirmar Importação"):
        df_import = pd.read_csv(uploaded_file)
        df_import['Usuario'] = st.session_state.usuario
        aba.append_rows(df_import.values.tolist())
        st.success("Dados importados!")
        st.rerun()
