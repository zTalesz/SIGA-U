import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from auth_utils import show_custom_menu
import sys
import os

# --- AUTENTICAÇÃO E MENU ---
show_custom_menu()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide")

# --- ESTILO CSS PARA OS CARTÕES ---
st.markdown("""
<style>
.metric-card {
    background-color: #FAFAFA;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #E0E0E0;
    text-align: center;
    color: #1E1E1E;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.metric-card .label {
    font-size: 1rem;
    color: #555555;
    margin-bottom: 0.5rem;
}
.metric-card .value {
    font-size: 2.5rem;
    font-weight: 600;
    color: #000000;
}
</style>
""", unsafe_allow_html=True)


st.title("🎓 Meu Painel")
st.write(f"Bem-vindo(a), *{st.session_state.user_info['nome_completo']}*!")

try:
    # --- CARREGAMENTO DE TODOS OS DADOS ---
    # CORREÇÃO: Caminhos absolutos e nomes de arquivo corretos
    df_usuarios = pd.read_csv('C:\Users\Tales\Desktop\PIM 2.0\PIM_STREAMLIT\data\usuarios.csv')
    df_turmas = pd.read_csv('C:\\Users\\luiso\\OneDrive\\Desktop\\PIM\\data\\turmas.csv')
    df_disciplinas = pd.read_csv('C:\\Users\\luiso\\OneDrive\\Desktop\\PIM\\data\\diciplinas.csv') 
    df_matriculas = pd.read_csv('C:\\Users\\luiso\\OneDrive\\Desktop\\PIM\\data\\matriculas.csv')
    df_notas = pd.read_csv('C:\\Users\\luiso\\OneDrive\\Desktop\\PIM\\data\\notas.csv')
    df_frequencia = pd.read_csv('C:\\Users\\luiso\\OneDrive\\Desktop\\PIM\\data\\frequencia.csv')

    # --- FILTRAGEM INICIAL DOS DADOS DO ALUNO LOGADO ---
    # CORREÇÃO: 'id_usuario' (chave do session_state)
    aluno_id = st.session_state.user_info['id_usuario'] 
    
    # CORREÇÃO: 'id_aluno' (coluna do matriculas.csv)
    matriculas_aluno = df_matriculas[df_matriculas['id_aluno'] == aluno_id]

    if matriculas_aluno.empty:
        st.warning("Você não está matriculado em nenhuma turma.")
    else:
        # --- SEÇÃO 1: MEU RESUMO ---
        st.header("Meu Resumo")
        
        # CORREÇÃO: 'id_matricula'
        notas_aluno_geral = df_notas[df_notas['id_matricula'].isin(matriculas_aluno['id_matricula'])]
        # CORREÇÃO: 'valor_nota'
        media_geral = notas_aluno_geral['valor_nota'].mean() if not notas_aluno_geral.empty else 0.0
        
        disciplinas_cursando = len(matriculas_aluno)
        
        # CORREÇÃO: 'id_matricula'
        frequencia_aluno_geral = df_frequencia[df_frequencia['id_matricula'].isin(matriculas_aluno['id_matricula'])]
        
        if not frequencia_aluno_geral.empty:
            # CORREÇÃO: 'status_presenca'
            presente_geral = (frequencia_aluno_geral['status_presenca'] == 'Presente').sum()
            taxa_presenca_geral = (presente_geral / len(frequencia_aluno_geral)) * 100
        else:
            taxa_presenca_geral = 0.0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="label">Média Geral</div><div class="value">{media_geral:.2f}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="label">Disciplinas Cursando</div><div class="value">{disciplinas_cursando}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="label">Taxa de Presença Geral</div><div class="value">{taxa_presenca_geral:.1f}%</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # --- SEÇÃO 2: ANÁLISE POR DISCIPLINA ---
        st.header("Análise por Disciplina")
        
        # CORREÇÃO LÓGICA: Revertido para a lógica original que agora está correta
        # CORREÇÃO: 'id_turma'
        disciplinas_do_aluno = pd.merge(matriculas_aluno, df_turmas, on='id_turma')
        # CORREÇÃO: 'id_disciplina'
        disciplinas_do_aluno = pd.merge(disciplinas_do_aluno, df_disciplinas, on='id_disciplina')
        
        disciplina_selecionada = st.selectbox(
            "Selecione uma disciplina para ver os detalhes:",
            # CORREÇÃO: 'nome_disciplina'
            options=disciplinas_do_aluno['nome_disciplina'].unique()
        )

        if disciplina_selecionada:
            # CORREÇÃO: 'nome_disciplina'
            info_disciplina = disciplinas_do_aluno[disciplinas_do_aluno['nome_disciplina'] == disciplina_selecionada].iloc[0]
            # CORREÇÃO: 'id_matricula'
            id_matricula_selecionada = info_disciplina['id_matricula']
            # CORREÇÃO: 'id_turma'
            id_turma_selecionada = info_disciplina['id_turma']

            col_d1, col_d2 = st.columns([1, 2])
            
            with col_d1:
                st.write("*Sua Frequência*")
                # CORREÇÃO: 'id_matricula'
                frequencia_disciplina = df_frequencia[df_frequencia['id_matricula'] == id_matricula_selecionada]
                if not frequencia_disciplina.empty:
                    # CORREÇÃO: 'status_presenca'
                    frequencia_counts = frequencia_disciplina['status_presenca'].value_counts().reset_index()
                    frequencia_counts.columns = ['status', 'contagem']
                    fig_donut_disciplina = px.pie(frequencia_counts, names='status', values='contagem',
                                                  title=f'Frequência',
                                                  color='status', color_discrete_map={'Presente': '#4285F4', 'Ausente': '#EA4335'}, hole=0.4)
                    fig_donut_disciplina.update_layout(margin=dict(t=30, b=0, l=0, r=0))
                    st.plotly_chart(fig_donut_disciplina, use_container_width=True)
                else:
                    st.info("Nenhum registro de frequência para esta matéria.")

            with col_d2:
                st.write("*Suas Notas*")
                # CORREÇÃO: 'id_matricula'
                notas_disciplina = df_notas[df_notas['id_matricula'] == id_matricula_selecionada]
                if not notas_disciplina.empty:
                    # CORREÇÃO: 'tipo_avaliacao' e 'valor_nota'
                    notas_display = notas_disciplina[['tipo_avaliacao', 'valor_nota']].rename(columns={'tipo_avaliacao': 'Avaliação', 'valor_nota': 'Nota'})
                    st.dataframe(notas_display, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma nota lançada para esta matéria.")

        st.markdown("---")

        # --- SEÇÃO 3: HORÁRIOS E PROFESSORES ---
        with st.expander("Ver meus horários e professores"):
            # CORREÇÃO: 'id_professor' e 'id_usuario'
            prof_info = pd.merge(disciplinas_do_aluno, df_usuarios, left_on='id_professor', right_on='id_usuario')
            
            # CORREÇÃO: Colunas 'nome_disciplina' e 'horario_sala'
            display_cols = ['nome_disciplina', 'nome_completo', 'horario_sala']
            st.dataframe(
                prof_info[display_cols].rename(columns={'nome_disciplina': 'Disciplina', 'nome_completo': 'Professor', 'horario_sala': 'Horário/Sala'}),
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown("---")

        # ######################################################################
        # ### NOVA SEÇÃO: CALENDÁRIO DE AULAS ###
        # ######################################################################
        st.header("Meu Calendário de Aulas")

        # CORREÇÃO: 'id_matricula'
        aulas_do_aluno = df_frequencia[df_frequencia['id_matricula'].isin(matriculas_aluno['id_matricula'])]
        
        # CORREÇÃO: 'id_matricula' e 'nome_disciplina'
        aulas_com_disciplina = pd.merge(
            aulas_do_aluno, 
            disciplinas_do_aluno[['id_matricula', 'nome_disciplina']], 
            on='id_matricula'
        )
        
        eventos_calendario = []
        for index, row in aulas_com_disciplina.iterrows():
            eventos_calendario.append({
                # CORREÇÃO: 'nome_disciplina'
                "title": row['nome_disciplina'], 
                "start": row['data_aula'],
                "end": row['data_aula'],
            })

        opcoes_calendario = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay",
            },
            "initialView": "dayGridMonth",
            "height": "700px",
        }
        calendar(events=eventos_calendario, options=opcoes_calendario)
except KeyError as e:
    st.error(f"ERRO DE COLUNA (KeyError): A coluna {e} não foi encontrada. Verifique os nomes das colunas nos seus arquivos CSV (ex: 'id_usuario', 'id_aluno', 'id_matricula', 'valor_nota', 'status_presenca', etc.).")
except FileNotFoundError as e:
    st.error(f"Arquivo de dados não encontrado: {e}. Verifique se o caminho e o nome do arquivo estão corretos.")
except Exception as e:
    st.error(f"Ocorreu um erro: {e}")