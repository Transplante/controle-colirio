import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Gestão de Colírios", layout="wide")

st.title("💧 Painel de Dilatação")

# Função de conexão usando o ID da planilha
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    # Abre diretamente pelo ID único da planilha
    return gc.open_by_key("1A1SViUbrg8Kx9sH0bT2pKn9P59fcpWNHRDXeXiQQNIc")

if 'usuario' not in st.session_state:
    st.subheader("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

try:
    sh = get_connection()
    # Acessa a aba pelo nome exato que aparece na planilha
    aba_registros = sh.worksheet("Registros")
    
    st.write(f"Conectado como: **{st.session_state.usuario}**")
    
    codigo = st.text_input("ID do Paciente:")
    if st.button("Confirmar Aplicação"):
        if codigo:
            aba_registros.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
            st.success("Registrado com sucesso!")
            st.rerun()
    
    st.subheader("📊 Histórico")
    dados = aba_registros.get_all_records()
    if dados:
        st.dataframe(pd.DataFrame(dados))
    else:
        st.info("Planilha vazia.")

except Exception as e:
    st.error(f"Erro ao conectar: {e}")
