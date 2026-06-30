import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Gestão de Colírios", layout="wide")

# Conexão Banco
conn = sqlite3.connect('clinica.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS pacientes (id_paciente TEXT PRIMARY KEY, nome TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY, 
                paciente_id TEXT, 
                horario TIMESTAMP, 
                usuario TEXT)''')
conn.commit()

# --- LOGIN SIMPLES ---
if 'usuario' not in st.session_state:
    st.title("🔐 Login Profissional")
    user = st.text_input("Usuário (Nome/Enfermeiro):")
    if st.button("Entrar"):
        if user:
            st.session_state.usuario = user
            st.rerun()
    st.stop()

st.title(f"💧 Painel de Dilatação - Operador: {st.session_state.usuario}")

# --- IMPORTAÇÃO E RESET ---
with st.expander("📂 Configurações"):
    col1, col2 = st.columns(2)
    with col1:
        arquivo = st.file_uploader("Upload CSV Pacientes", type=['csv'])
        if arquivo:
            df = pd.read_csv(arquivo)
            for _, row in df.iterrows():
                c.execute("INSERT OR REPLACE INTO pacientes (id_paciente, nome) VALUES (?, ?)", (str(row['ID']), str(row['Nome'])))
            conn.commit()
    with col2:
        if st.button("🔴 LIMPAR TUDO"):
            c.execute("DELETE FROM registros")
            c.execute("DELETE FROM pacientes")
            conn.commit()
            st.rerun()

# --- REGISTRO ---
codigo = st.text_input("Bipe/Digite ID do Paciente:")
if codigo:
    c.execute("SELECT nome FROM pacientes WHERE id_paciente = ?", (codigo,))
    if c.fetchone():
        c.execute("INSERT INTO registros (paciente_id, horario, usuario) VALUES (?, ?, ?)", 
                  (codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario))
        conn.commit()
        st.success("Gota registrada!")
    else:
        st.error("Paciente não encontrado!")

# --- PAINEL DETALHADO ---
st.subheader("📊 Status Detalhado")
pacientes = c.execute("SELECT id_paciente, nome FROM pacientes").fetchall()

for pid, nome in pacientes:
    # Busca histórico
    hist = c.execute("SELECT horario, usuario FROM registros WHERE paciente_id = ? ORDER BY horario DESC", (pid,)).fetchall()
    total = len(hist)
    
    status_cor, texto = "🔴", "Não Dilatado"
    if hist:
        ultima_data = datetime.strptime(hist[0][0], "%Y-%m-%d %H:%M:%S")
        diff = (datetime.now() - ultima_data).total_seconds() / 60
        if diff < 2: status_cor, texto = "🔴", "Dilatando..."
        elif diff < 5: status_cor, texto = "🟡", "Aguardando..."
        else: status_cor, texto = "🟢", "Pronto!"
        
        ultima_gota = f"Última: {hist[0][0]} por {hist[0][1]}"
    else:
        ultima_gota = "Nenhuma gota aplicada."

    # Exibição visual
    with st.container(border=True):
        st.markdown(f"### {status_cor} {nome} (ID: {pid})")
        st.write(f"**Total de gotas:** {total} | **Status:** {texto}")
        st.write(f"*{ultima_gota}*")
        if total > 0:
            with st.expander("Ver histórico de aplicações"):
                for h in hist:
                    st.write(f"- {h[0]} aplicado por {h[1]}")
