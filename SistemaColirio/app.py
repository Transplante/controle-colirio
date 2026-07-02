# 2. APLICAÇÕES (CORRIGIDO)
with tabs[1]:
    st.header("Registrar Gota")
    id_pac = st.text_input("ID do Paciente:")
    
    if st.button("Confirmar Aplicação"):
        if id_pac:
            # 1. Filtra o dataframe para ver se o ID já existe
            paciente_existente = df[df['PacienteID'].astype(str) == str(id_pac)]
            
            if not paciente_existente.empty:
                # Se existe, acha a linha (índice + 2, pois o Gsheets começa na linha 1 + cabeçalho)
                # O gspread usa índice 1 para a primeira linha
                idx = paciente_existente.index[0]
                linha_planilha = idx + 2 
                
                # Pega o valor atual de gotas e soma 1
                gotas_atuais = int(paciente_existente.iloc[0]['QuantidadeGotas'])
                nova_qtd = gotas_atuais + 1
                
                # Atualiza apenas a célula da coluna 3 (QuantidadeGotas)
                aba.update_cell(linha_planilha, 3, nova_qtd)
                st.success(f"Gota registrada para ID {id_pac}!")
            else:
                # Se não existe, cria nova linha
                aba.append_row([id_pac, "Novo Paciente", 1, st.session_state.usuario])
                st.success("Novo paciente criado e gota registrada!")
            
            st.rerun()
            
    st.dataframe(df, use_container_width=True, hide_index=True)
