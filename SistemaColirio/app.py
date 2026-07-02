import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestão de Colírios", layout="wide")

# Conexão com Google Sheets usando as credenciais do "Secrets"
@st.cache_resource
def get_connection():
    # Puxa o dicionário de credenciais configurado no painel "Secrets"
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    # Abre a planilha pelo nome (verifique se está exatamente igual no Google Drive)
    return gc.open("Planilha sem título")

st.title("💧 Painel de Dilatação")

# --- LOGIN ---
if 'usuario' not in st.session_state:
    st.subheader("🔐 Login Profissional")
    user = st.text_input("Nome do Operador:")
    if st.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

st.write(f"Operador logado: **{st.session_state.usuario}**")

# --- REGISTRO ---
try:
    sh = get_connection()
    # Certifique-se de que a aba na planilha se chama exatamente "Registros"
    aba_registros = sh.worksheet("Registros")
    
    st.subheader("Registrar Paciente")
    codigo = st.text_input("Bipe/Digite ID do Paciente:")
    
    if st.button("Confirmar Aplicação"):
        if codigo:
            # Adiciona linha: ID, Data/Hora, Operador
            aba_registros.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
            st.success(f"Gota registrada para o paciente {codigo}!")
        else:
            st.warning("Por favor, digite o ID do paciente.")

    # --- EXIBIÇÃO ---
    st.divider()
    st.subheader("📊 Últimos 10 Registros")
    
    # Busca os dados
    dados = aba_registros.get_all_records()
    if dados:
        df = pd.DataFrame(dados)
        # Exibe os últimos 10 de forma invertida
        st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)
    else:
        st.info("Nenhum registro encontrado.")
        
except Exception as e:
    st.error(f"Erro ao acessar a planilha: {e}")
    st.info("Dica: Verifique se a aba 'Registros' existe e se o e-mail do 'client_email' é Editor na planilha.")
