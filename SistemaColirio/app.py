import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Gestão de Dilatação", layout="wide")

st.title("💧 Painel de Dilatação")

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

tabs = st.tabs(["🏠 Dashboard", "💧 Aplicações", "📥 Importar"])

dados, aba = ler_dados()
df = pd.DataFrame(dados)

# 1. DASHBOARD: Lista dinâmica com lógica de Status
with tabs[0]:
    st.header("🏠 Monitoramento em Tempo Real")
    
    if not df.empty:
        # Conta quantas gotas (linhas) cada PacienteID tem
        contagem = df['PacienteID'].value_counts()
        
        for paciente_id, total_gotas in contagem.items():
            # Lógica de Status
            if 1 <= total_gotas <= 3:
                status = "🟢 Não está dilatado"
                cor = st.info
            elif 4 <= total_gotas <= 8:
                status = "🟡 Quase dilatado"
                cor = st.warning
            else: # 9 ou mais
                status = "🔴 Dilatado"
                cor = st.error
            
            cor(f"**Paciente: {paciente_id}** | Gotas: {total_gotas} | Status: {status}")
    else:
        st.info("Nenhum paciente registrado.")

# 2. APLICAÇÕES
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
