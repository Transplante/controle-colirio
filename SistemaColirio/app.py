import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestão de Colírios", layout="wide")

# Conexão com Google Sheets usando as credenciais do "Secrets"
@st.cache_resource
def get_connection():
    # Puxa as credenciais que você configurou no painel "Secrets" do Streamlit Cloud
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    # Abre sua planilha pelo nome
    return gc.open("Planilha sem título")

st.title("💧 Painel de Dilatação")

# --- LOGIN ---
if 'usuario' not in st.session_state:
    st.title("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

st.write(f"Operador logado: **{st.session_state.usuario}**")

# --- REGISTRO ---
try:
    sh = get_connection()
    aba_registros = sh.worksheet("Registros")
    
    codigo = st.text_input("Bipe/Digite ID do Paciente:")
    if codigo:
        # Registra ID, Horário e Usuário na planilha
        aba_registros.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
        st.success(f"Gota registrada para o paciente {codigo}!")
        st.rerun()

    # --- EXIBIÇÃO ---
    st.subheader("📊 Histórico de Aplicações")
    # Busca todos os dados da aba "Registros"
    dados = aba_registros.get_all_records()
    if dados:
        df = pd.DataFrame(dados)
        st.dataframe(df.tail(10)) # Mostra as últimas 10 entradas
    else:
        st.info("Nenhum registro encontrado ainda.")
        
except Exception as e:
    st.error(f"Erro ao conectar na planilha. Verifique se o e-mail do 'client_email' foi compartilhado na planilha como Editor. Detalhes: {e}")
