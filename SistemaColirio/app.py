import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Gestão de Colírios", layout="wide")

st.title("💧 Painel de Dilatação")

# Conexão com Google Sheets
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key("1A1SViUbrg8Kx9sH0bT2pKn9P59fcpWNHRDXeXiQQNIc")

@st.cache_data(ttl=1)
def ler_dados():
    sh = get_connection()
    aba = sh.worksheet("Registros")
    return aba.get_all_records(), aba

# --- LOGIN ---
if 'usuario' not in st.session_state:
    st.subheader("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

st.write(f"Operador logado: **{st.session_state.usuario}**")

try:
    dados, aba = ler_dados()
    
    # --- ÁREA DE IMPORTAÇÃO (HIPERDOCTOR) ---
    with st.expander("📥 Importar dados do HiperDoctor"):
        uploaded_file = st.file_uploader("Escolha o arquivo CSV do HiperDoctor", type=["csv"])
        if uploaded_file:
            df_import = pd.read_csv(uploaded_file)
            st.write("Prévia dos dados:")
            st.dataframe(df_import.head())
            
            if st.button("Confirmar Importação para a Planilha"):
                # Transforma o CSV em lista para o Google Sheets
                dados_lista = df_import.values.tolist()
                aba.append_rows(dados_lista)
                st.success("Dados do HiperDoctor importados com sucesso!")
                st.rerun()

    # --- REGISTRO MANUAL ---
    st.divider()
    st.subheader("Registrar Paciente")
    codigo = st.text_input("ID do Paciente:")
    if st.button("Confirmar Aplicação"):
        if codigo:
            aba.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
            st.success("Registrado!")
            st.rerun()

    # --- LIMPEZA ---
    if st.button("🧹 Limpar Histórico Completo"):
        aba.delete_rows(2, aba.row_count)
        st.warning("Histórico apagado!")
        st.rerun()

    # --- EXIBIÇÃO ---
    st.subheader("📊 Histórico")
    if dados:
        st.dataframe(pd.DataFrame(dados), use_container_width=True)
    else:
        st.info("Planilha vazia.")

except Exception as e:
    st.error(f"Erro: {e}")
