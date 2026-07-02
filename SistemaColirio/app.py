# 1. DASHBOARD: Lista dinâmica com lógica de Status invertida
with tabs[0]:
    st.header("🏠 Monitoramento em Tempo Real")
    
    if not df.empty:
        # Conta quantas vezes cada PacienteID aparece (cada registro é uma gota)
        contagem = df['PacienteID'].value_counts()
        
        for paciente_id, total_gotas in contagem.items():
            # Nova lógica de Status:
            # 1 a 3 gotas: Vermelho (não dilatado)
            # 4 a 8 gotas: Amarelo (quase dilatado)
            # 9 ou mais gotas: Verde (dilatado)
            
            if 1 <= total_gotas <= 3:
                status = "🔴 Não está dilatado"
                cor = st.error # Vermelho
            elif 4 <= total_gotas <= 8:
                status = "🟡 Quase dilatado"
                cor = st.warning # Amarelo
            else: 
                status = "🟢 Dilatado"
                cor = st.success # Verde
            
            cor(f"**Paciente: {paciente_id}** | Gota atual: {total_gotas}ª | Status: {status}")
    else:
        st.info("Nenhum paciente registrado.")
