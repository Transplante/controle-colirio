import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Painel de Dilatação Pro", layout="wide")

# Conexão
@st.cache_resource
def get_connection():
    creds = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key("1A1SViUbrg8Kx9sH0bT2pKn9P59fcpWNHRDXeXiQQNIc")

# Carrega os dados da aba "Registros"
def ler_dados():
    sh = get_connection()
    aba = sh.worksheet("Registros")
    return pd.DataFrame(aba.get_all_records()), aba

# Login
if 'usuario' not in st.session_state:
    st.sidebar.text_input("Seu Nome:", key="temp_user")
    if st.sidebar.button("Entrar"):
        st.session_state.usuario = st.session_state.temp_user
        st.rerun()
    st.stop()

tabs = st.tabs(["🏠 Dashboard", "💧 Aplicações", "📥 Importar"])

df, aba = ler_dados()

# 1. DASHBOARD: Cartões organizados por paciente
with tabs[0]:
    st.header("🏠 Monitoramento de Pacientes")
    if not df.empty:
        # Cria colunas para organizar os cartões lado a lado
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                # Lógica de cores baseada na quantidade de gotas
                gotas = int(row['QuantidadeGotas'])
                if gotas <= 3:
                    cor = st.error # Vermelho (Não dilatado)
                elif 4 <= gotas <= 8:
                    cor = st.warning # Amarelo (Quase)
                else:
                    cor = st.success # Verde (Dilatado)
                
                cor(f"**{row['NomePaciente']}**\n\nID: {row['PacienteID']}\nGotas: {gotas}/10\nResponsável: {row['Usuario']}")
    else:
        st.info("Nenhum paciente registrado.")

# 2. APLICAÇÕES: Registro individual
with tabs[1]:
    st.header("Registrar Aplicação")
    paciente_id = st.text_input("ID do Paciente")
    if st.button("Confirmar Gota"):
        # Adiciona nova linha
        aba.append_row([paciente_id, "Nome Exemplo", 1, st.session_state.usuario])
        st.rerun()
    st.dataframe(df)

# 3. IMPORTAR: Aqui fixamos o nome de quem importa
with tabs[2]:
    st.header("📥 Importação HiperDoctor")
    uploaded_file = st.file_uploader("CSV do HiperDoctor", type=["csv"])
    if uploaded_file:
        df_import = pd.read_csv(uploaded_file)
        if st.button("Confirmar Importação"):
            # Adiciona a coluna de usuário com o nome de quem está logado
            df_import['Usuario'] = st.session_state.usuario
            aba.append_rows(df_import.values.tolist())
            st.success("Dados importados com o seu nome!")
            st.rerun()
