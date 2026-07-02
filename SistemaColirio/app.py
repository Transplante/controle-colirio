import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestão de Colírios", layout="wide")

st.title("💧 Painel de Dilatação")

# --- CONEXÃO ---
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open("Gestão De Colírios") # Nome exato da sua planilha

# --- LOGIN ---
if 'usuario' not in st.session_state:
    st.subheader("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

st.write(f"Operador logado: **{st.session_state.usuario}**")

# --- REGISTRO E EXIBIÇÃO ---
try:
    sh = get_connection()
    aba_registros = sh.worksheet("Registros")
    
    st.subheader("Registrar Paciente")
    codigo = st.text_input("Bipe/Digite ID do Paciente:")
    
    if st.button("Confirmar Aplicação"):
        if codigo:
            aba_registros.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
            st.success(f"Gota registrada para o paciente {codigo}!")
            st.rerun()
        else:
            st.warning("Por favor, digite o ID do paciente.")

    st.divider()
    st.subheader("📊 Últimos Registros")
    dados = aba_registros.get_all_records()
    if dados:
        df = pd.DataFrame(dados)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado.")
        
except Exception as erro_msg:
    st.error(f"Erro ao acessar a planilha: {erro_msg}")
