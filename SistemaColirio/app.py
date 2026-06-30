import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# Configurações iniciais
st.set_page_config(page_title="Gestão de Colírios", layout="wide")

# Conexão com Google Sheets (usando credenciais configuradas no Streamlit Cloud)
def get_connection():
    # Isso busca as credenciais que você vai configurar no Streamlit Cloud (Secrets)
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open("Planilha sem título").worksheet("Registros")

# --- LOGIN ---
if 'usuario' not in st.session_state:
    st.title("🔐 Login Profissional")
    user = st.text_input("Usuário:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

st.title(f"💧 Painel de Dilatação - Operador: {st.session_state.usuario}")

# --- REGISTRO ---
codigo = st.text_input("Bipe/Digite ID do Paciente:")
if codigo:
    try:
        sh = get_connection()
        # Adiciona nova linha na planilha de Registros
        sh.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
        st.success(f"Gota registrada para o paciente {codigo}!")
    except Exception as e:
        st.error(f"Erro ao conectar na planilha: {e}")

# --- EXIBIÇÃO ---
st.subheader("📊 Últimos Registros")
try:
    sh = get_connection()
    dados = pd.DataFrame(sh.get_all_records())
    st.dataframe(dados.tail(10)) # Mostra as últimas 10 aplicações
except:
    st.warning("Aguardando registros...")
