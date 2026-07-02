import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Gestão de Dilatação", layout="wide")

st.title("💧 Painel de Dilatação")

# Conexão
@st.cache_resource
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key("1A1SViUbrg8Kx9sH0bT2pKn9P59fcpWNHRDXeXiQQNIc")

@st.cache_data(ttl=1)
def ler_dados():
    sh = get_connection()
    aba_reg = sh.worksheet("Registros")
    return aba_reg.get_all_records(), aba_reg

if 'usuario' not in st.session_state:
    st.subheader("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

# Abas do sistema
tabs = st.tabs(["🏠 Dashboard", "💧 Aplicações", "📥 Importar"])

dados, aba = ler_dados()
df = pd.DataFrame(dados)

# 1. DASHBOARD: Lista dinâmica espelhada da planilha
with tabs[0]:
    st.header("🏠 Monitoramento em Tempo Real")
    total_pacientes = df['PacienteID'].nunique() if not df.empty else 0
    st.metric("👥 Pacientes atendidos hoje", total_pacientes)
    st.divider()

    if not df.empty:
        # Percorre cada linha da planilha para criar um cartão no Dashboard
        for index, row in df.iterrows():
            status_text = f"Paciente: {row['PacienteID']} | Operador: {row['Usuario']} | Horário: {row['Horario']}"
            
            # Aqui aplicamos a lógica visual (exemplo simples de cor)
            # Você pode criar uma coluna 'Status' na sua planilha para controlar isso
            st.info(f"🟢 {status_text}") 
    else:
        st.info("Nenhum paciente registrado no momento.")

# 2. APLICAÇÕES: Onde você insere os dados que aparecem no Dashboard
with tabs[1]:
    st.header("💧 Registro de Gotas")
    codigo = st.text_input("ID do Paciente:")
    if st.button("Confirmar Aplicação"):
        if codigo:
            aba.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
            st.rerun()
    st.dataframe(df, use_container_width=True)

# 3. IMPORTAR
with tabs[2]:
    st.header("📥 Importação HiperDoctor")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file and st.button("Processar"):
        df_import = pd.read_csv(uploaded_file)
        aba.append_rows(df_import.values.tolist())
        st.rerun()
