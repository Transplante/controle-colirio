import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Gestão de Colírios", layout="wide")

st.title("💧 Painel de Dilatação")

# Função de conexão
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key("1A1SViUbrg8Kx9sH0bT2pKn9P59fcpWNHRDXeXiQQNIc")

# Força o Streamlit a buscar dados novos da planilha constantemente
@st.cache_data(ttl=1)
def ler_dados():
    sh = get_connection()
    aba = sh.worksheet("Registros")
    return aba.get_all_records(), aba

if 'usuario' not in st.session_state:
    st.subheader("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

st.write(f"Conectado como: **{st.session_state.usuario}**")

try:
    dados, aba = ler_dados()
    
    # --- REGISTRO ---
    codigo = st.text_input("ID do Paciente:")
    if st.button("Confirmar Aplicação"):
        if codigo:
            aba.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
            st.success("Registrado!")
            st.rerun()
    
    # --- LIMPEZA DE HISTÓRICO ---
    if st.button("🧹 Limpar Histórico Completo"):
        # Limpa da linha 2 em diante (mantém cabeçalho na linha 1)
        aba.delete_rows(2, aba.row_count)
        st.warning("Histórico apagado!")
        st.rerun()

    st.subheader("📊 Histórico")
    if dados:
        st.dataframe(pd.DataFrame(dados), use_container_width=True)
    else:
        st.info("Planilha vazia.")

except Exception as e:
    st.error(f"Erro: {e}")
