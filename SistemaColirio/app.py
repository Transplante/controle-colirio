import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

st.set_page_config(page_title="Gestão de Dilatação", layout="wide")

@st.cache_resource
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key("1A1SViUbrg8Kx9sH0bT2pKn9P59fcpWNHRDXeXiQQNIc")

def ler_dados():
    sh = get_connection()
    aba = sh.worksheet("Registros")
    data = aba.get_all_records()
    df = pd.DataFrame(data)
    return df, aba

# Login
if 'usuario' not in st.session_state:
    st.sidebar.title("🔐 Login")
    user = st.sidebar.text_input("Seu Nome:")
    if st.sidebar.button("Entrar") and user:
        st.session_state.usuario = user
        st.rerun()
    st.stop()

# Abas
tabs = st.tabs(["🏠 Dashboard", "💧 Aplicações", "📥 Importar"])
df, aba = ler_dados()

# 1. DASHBOARD
with tabs[0]:
    st.header("🏠 Monitoramento")
    if not df.empty:
        # Força conversão para numérico para evitar erros
        df['QuantidadeGotas'] = pd.to_numeric(df['QuantidadeGotas'], errors='coerce').fillna(0)
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                gotas = int(row['QuantidadeGotas'])
                label = f"ID: {row.get('PacienteID', 'N/A')} | Gotas: {gotas}/10"
                if gotas <= 3: st.error("🔴 " + label)
                elif gotas <= 8: st.warning("🟡 " + label)
                else: st.success("🟢 " + label)

# 2. APLICAÇÕES
with tabs[1]:
    st.header("Registrar Gota")
    id_pac = st.text_input("ID do Paciente:")
    if st.button("Confirmar Aplicação"):
        if id_pac_id:
            aba.append_row([id_pac, "N/A", 1, st.session_state.usuario])
            st.rerun()
    st.dataframe(df, use_container_width=True, hide_index=True)

# 3. IMPORTAR (Mapeamento manual)
with tabs[2]:
    st.header("📥 Importação HiperDoctor")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        if st.button("Processar Importação"):
            df_import = pd.read_csv(uploaded_file)
            
            # --- MAPEAMENTO MANUAL ---
            # Aqui ajustamos para pegar os dados do seu CSV. 
            # Verifique se o seu CSV tem colunas chamadas 'ID' e 'Nome'
            # Se forem outros nomes, altere aqui:
            df_final = pd.DataFrame()
            df_final['PacienteID'] = df_import.iloc[:, 0]  # Pega a 1ª coluna do CSV como ID
            df_final['NomePaciente'] = df_import.iloc[:, 1] # Pega a 2ª coluna como Nome
            df_final['QuantidadeGotas'] = 0                # Começa zerado
            df_final['Usuario'] = st.session_state.usuario  # Registra o nome do logado
            
            aba.append_rows(df_final.values.tolist())
            st.success("Importação concluída com sucesso!")
            st.rerun()
