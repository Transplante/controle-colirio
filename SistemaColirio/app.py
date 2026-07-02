# --- REGISTRO ---
try:
    sh = get_connection()
    aba_registros = sh.worksheet("Registros")
    
    st.subheader("Registrar Paciente")
    codigo = st.text_input("Bipe/Digite ID do Paciente:")
    
    if st.button("Confirmar Aplicação"):
        if codigo:
            # Garante que vai inserir na ordem correta das suas colunas: PacienteID, Horario, Usuario
            aba_registros.append_row([codigo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.usuario])
            st.success(f"Gota registrada para o paciente {codigo}!")
        else:
            st.warning("Por favor, digite o ID do paciente.")

    # --- EXIBIÇÃO ---
    st.divider()
    st.subheader("📊 Últimos Registros")
    
    # get_all_records pega os cabeçalhos automaticamente
    dados = aba_registros.get_all_records()
    
    if dados:
        df = pd.DataFrame(dados)
        # Exibe o DataFrame. Como você já tem dados, ele vai mostrar a tabela
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado.")
        
except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
