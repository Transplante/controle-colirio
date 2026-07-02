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

@st.cache_data(ttl=1)
def ler_dados():
    sh = get_connection()
    aba_reg = sh.worksheet("Registros")
    return aba_reg.get_all_records(), aba_reg

# Login
if 'usuario' not in st.session_state:
    st.sidebar.title("🔐 Login")
    user = st.sidebar.text_input("Nome do Operador:")
    if st.sidebar.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

# --- SIDEBAR (Configurações e Limpeza) ---
with st.sidebar:
    st.title("💧 Painel de Dilatação")
    st.write(f"Operador: **{st.session_state.usuario}**")
    st.divider()
    
    if st.button("🧹 Limpar Histórico"):
        sh = get_connection()
        aba = sh.worksheet("Registros")
        if aba.row_count > 1:
            aba.delete_rows(2, aba.row_count)
            st.warning("Histórico apagado!")
            st.rerun()
        else:
            st.info("A planilha já está vazia!")

# --- DEFINIÇÃO DAS ABAS ---
tabs = st.tabs(["🏠 Dashboard", "💧 Aplicações", "📥 Importar"])

# Carrega dados
dados, aba = ler_dados()
df = pd.DataFrame(dados)

# 1. DASHBOARD
with tabs[0]:
    st.header("🏠 Monitoramento em Tempo Real")
    if not df.empty:
        contagem = df.groupby('PacienteID').size()
        cols = st.columns(3) 
        for i, (paciente_id, total_gotas) in enumerate(contagem.items()):
            with cols[i % 3]:
                # Lógica: 1-3 Vermelho, 4-8 Amarelo, 9+ Verde
                if 1 <= total_gotas <= 3:
                    st.error(f"🔴 **ID: {paciente_id}**\n\nGota: {total_gotas}ª\n\nStatus: Não dilatado")
                elif 4 <= total_gotas <= 8:
                    st.warning(f"🟡 **ID: {paciente_id}**\n\nGota: {total_gotas}ª\n\nStatus: Quase dilatado")
                else:
                    st.success(f"🟢 **ID: {paciente_id}**\n\nGota: {total_gotas}ª\n\nStatus: Dilatado")
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
    if uploaded_file and st.button("Processar Importação"):
        df_import = pd.read_csv(uploaded_file)
        aba.append_rows(df_import.values.tolist())
        st.rerun()
