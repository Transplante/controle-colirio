import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Controle de Colírios", layout="wide")

# Conexão Banco
conn = sqlite3.connect('clinica.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS pacientes (id_paciente TEXT PRIMARY KEY, nome TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS registros (id INTEGER PRIMARY KEY, paciente_id TEXT, horario TIMESTAMP)''')
conn.commit()

# Título
st.title("💧 Painel de Monitoramento de Dilatação")

# --- ÁREA DE ADMINISTRAÇÃO ---
with st.expander("📂 Configurações de Dados"):
    col1, col2 = st.columns(2)
    with col1:
        arquivo = st.file_uploader("Importar CSV (ID, Nome)", type=['csv'])
        if arquivo:
            df = pd.read_csv(arquivo)
            for _, row in df.iterrows():
                c.execute("INSERT OR REPLACE INTO pacientes (id_paciente, nome) VALUES (?, ?)", (str(row['ID']), str(row['Nome'])))
            conn.commit()
            st.success("Pacientes carregados!")
    with col2:
        if st.button("🔴 APAGAR TODOS OS DADOS (RESET)"):
            c.execute("DELETE FROM registros")
            c.execute("DELETE FROM pacientes")
            conn.commit()
            st.rerun()

# --- REGISTRO DE BIPS ---
codigo = st.text_input("Bipe o código do paciente:", key="bip")
if codigo:
    c.execute("SELECT nome FROM pacientes WHERE id_paciente = ?", (codigo,))
    paciente = c.fetchone()
    if paciente:
        c.execute("SELECT horario FROM registros WHERE paciente_id = ? ORDER BY id DESC LIMIT 1", (codigo,))
        ultima = c.fetchone()
        if not ultima or (datetime.now() - datetime.strptime(ultima[0], "%Y-%m-%d %H:%M:%S")).total_seconds() > 10:
            c.execute("INSERT INTO registros (paciente_id, horario) VALUES (?, ?)", (codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            st.rerun()
    else:
        st.error("⚠️ Paciente não encontrado!")

# --- PAINEL DE STATUS ---
st.subheader("📊 Status dos Pacientes")
pacientes = c.execute("SELECT id_paciente, nome FROM pacientes").fetchall()

for pid, nome in pacientes:
    c.execute("SELECT horario FROM registros WHERE paciente_id = ? ORDER BY id DESC LIMIT 1", (pid,))
    ultima = c.fetchone()
    c.execute("SELECT count(*) FROM registros WHERE paciente_id = ?", (pid,))
    total = c.fetchone()[0]

    status_cor, texto = "🔴", "Não Dilatado"
    if ultima:
        diff = (datetime.now() - datetime.strptime(ultima[0], "%Y-%m-%d %H:%M:%S")).total_seconds() / 60
        if diff < 2: status_cor, texto = "🔴", "Dilatando..."
        elif diff < 5: status_cor, texto = "🟡", "Aguardando..."
        else: status_cor, texto = "🟢", "Pronto!"

    st.markdown(f"### {status_cor} {nome} (ID: {pid})")
    st.write(f"Total de gotas: **{total}** | Status: **{texto}**")
    st.divider()

# Para atualizar a tela sozinho sem travar, use o comando abaixo no terminal:
# streamlit run app.py --server.runOnSave true