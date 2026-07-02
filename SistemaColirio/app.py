import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Gestão de Colírios", layout="wide")

st.title("💧 Painel de Dilatação")

def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open("Gestão De Colírios")

if 'usuario' not in st.session_state:
    st.subheader("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

try:
    sh = get_connection()
    # Listar nomes das abas para identificar qual é a correta
    abas = [aba.title for aba in sh.worksheets()]
    
    # Tenta usar a aba 'Registros', se não existir, avisa qual nome o script enxergou
    if "Registros" in abas:
        aba_registros = sh.worksheet("Registros")
        
        st.subheader("Registrar Paciente")
        codigo = st.text_input("Bipe/Digite ID do Paciente:")
        
        if st.button("Confirmar Aplicação"):
            if codigo:
                aba_registros.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
                st.success("Registrado!")
                st.rerun()
        
        st.divider()
        st.subheader("📊 Últimos Registros")
        dados = aba_registros.get_all_records()
        if dados:
            st.dataframe(pd.DataFrame(dados))
    else:
        st.error(f"A aba 'Registros' não foi encontrada. Abas disponíveis na planilha: {abas}")

except Exception as erro_msg:
    st.error(f"Erro detalhado: {erro_msg}")
