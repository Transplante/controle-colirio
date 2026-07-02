import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Sistema de Dilatação Pro", layout="wide")

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

# --- LOGIN ---
if 'usuario' not in st.session_state:
    st.subheader("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

# --- ESTRUTURA MODULAR ---
tabs = st.tabs(["🏠 Dashboard", "💧 Aplicações", "📥 Importar", "⚙️ Protocolos"])

# 1. DASHBOARD
with tabs[0]:
    st.header("🏠 Monitoramento em Tempo Real")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Em dilatação", "18")
    c2.metric("💧 Gotas hoje", "426")
    c3.metric("⏰ Próxima", "08:35")
    c4.metric("⚠ Atraso", "2")
    
    st.divider()
    # Exemplo de Cards de Sala
    col1, col2 = st.columns(2)
    col1.info("🟢 **João Silva** - Sala 02 | 18/32 gotas | Próxima: 08:35")
    col2.error("🔴 **Carlos Souza** - Sala 03 | ATRASADO | Ação Imediata!")

# 2. APLICAÇÕES (Registro Manual + Histórico)
with tabs[1]:
    st.header("💧 Registro de Gotas")
    dados, aba = ler_dados()
    
    codigo = st.text_input("ID do Paciente:")
    if st.button("Confirmar Aplicação"):
        if codigo:
            aba.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
            st.success("Registrado!")
            st.rerun()
    
    st.subheader("📊 Histórico Completo")
    if dados:
        st.dataframe(pd.DataFrame(dados), use_container_width=True)

# 3. IMPORTAR (HiperDoctor)
with tabs[2]:
    st.header("📥 Importação em Massa")
    uploaded_file = st.file_uploader("Upload CSV do HiperDoctor", type=["csv"])
    if uploaded_file:
        df_import = pd.read_csv(uploaded_file)
        if st.button("Confirmar Importação"):
            aba.append_rows(df_import.values.tolist())
            st.success("Dados importados!")
            st.rerun()

# 4. PROTOCOLOS
with tabs[3]:
    st.header("⚙️ Configurar Protocolos")
    with st.form("protocolo_form"):
        nome = st.text_input("Nome do Protocolo")
        qtd = st.number_input("Quantidade de gotas", 1, 50)
        submit = st.form_submit_button("Salvar Protocolo")
        if submit:
            st.success(f"Protocolo {nome} salvo.")
    
    if st.button("🧹 Limpar Histórico Completo"):
        aba.delete_rows(2, aba.row_count)
        st.warning("Histórico apagado!")
        st.rerun()
