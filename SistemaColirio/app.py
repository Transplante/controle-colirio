# 3. IMPORTAR
with tabs[2]:
    st.header("📥 Importação")
    uploaded_file = st.file_uploader("CSV do HiperDoctor", type=["csv"])
    
    if uploaded_file is not None:
        if st.button("Processar Importação"):
            # Lê o CSV
            df_import = pd.read_csv(uploaded_file)
            
            # ADICIONE ESTA LINHA: Garante que a coluna Usuario receba o nome do logado
            df_import['Usuario'] = st.session_state.usuario
            
            # Se a coluna QuantidadeGotas não existir no CSV, cria ela com 0
            if 'QuantidadeGotas' not in df_import.columns:
                df_import['QuantidadeGotas'] = 0
            
            # Adiciona os dados na planilha
            aba.append_rows(df_import.values.tolist())
            st.success("Importado com sucesso!")
            st.rerun()
