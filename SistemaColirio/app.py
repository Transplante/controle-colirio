# --- BOTÃO NO SIDEBAR (CORRIGIDO) ---
with st.sidebar:
    st.title("💧 Painel de Dilatação")
    st.write(f"Operador: **{st.session_state.usuario}**")
    st.divider()
    
    if st.button("🧹 Limpar Histórico"):
        # Obtém a conexão novamente dentro do botão para garantir que está atualizada
        sh = get_connection()
        aba = sh.worksheet("Registros")
        
        # Verifica se há linhas para deletar antes de tentar
        total_linhas = aba.row_count
        if total_linhas > 1:
            try:
                # Deleta da linha 2 até a última linha existente
                aba.delete_rows(2, total_linhas)
                st.success("Histórico apagado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao limpar: {e}")
        else:
            st.info("A planilha já está vazia!")
