# pages/painel_professor.py (ATUALIZADO E INTELIGENTE)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# 1. Bloco de importação de path (sys.path)
pages_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(pages_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 2. Imports das suas bibliotecas
from auth_utils import show_custom_menu
from config import get_csv_path

# 3. COMANDO Nº 1: st.set_page_config()
st.set_page_config(layout="wide")

# 4. COMANDO Nº 2: show_custom_menu()
show_custom_menu()

# --- ESTILO CSS PARA OS CARTÕES ---
st.markdown("""
<style>
.metric-card {
    background-color: #FAFAFA; padding: 1.5rem; border-radius: 10px; border: 1px solid #E0E0E0;
    text-align: center; color: #1E1E1E; height: 100%; display: flex; flex-direction: column; justify-content: center;
}
.metric-card .label { font-size: 1rem; color: #555555; margin-bottom: 0.5rem; }
.metric-card .value { font-size: 2.5rem; font-weight: 600; color: #000000; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# LÓGICA DE VISUALIZAÇÃO DE ACORDO COM O PERFIL
# ==========================================================

# 1. Pega o perfil do usuário logado
user_role = st.session_state.user_info['role']
user_id = st.session_state.user_info['id_usuario']
user_name = st.session_state.user_info['nome_completo']

# 2. Prepara a variável do ID do professor que vamos exibir
professor_id_para_exibir = None
nome_professor_para_exibir = ""

try:
    # Carregamos o 'usuarios.csv' primeiro, pois é essencial para a lógica
    df_usuarios = pd.read_csv(get_csv_path('usuarios.csv'))
except FileNotFoundError:
    st.error(f"Arquivo 'usuarios.csv' não encontrado.")
    st.stop()


# 3. Decide qual ID de professor vamos usar
if user_role == 'Professor':
    st.title("🧑‍🏫 Meu Painel")
    st.write(f"Olá, Prof(a). *{user_name}*!")
    professor_id_para_exibir = int(user_id)
    nome_professor_para_exibir = user_name

elif user_role in ['Coordenação', 'Administração']:
    st.title("🔍 Visualizador de Painel de Professor")
    st.info(f"Logado como {user_role}. Selecione um professor para visualizar seu painel.")
    
    # Pega todos os professores do CSV
    lista_professores = df_usuarios[df_usuarios['role'] == 'Professor'][['nome_completo', 'id_usuario']]
    
    if lista_professores.empty:
        st.error("Nenhum professor cadastrado no sistema.")
        st.stop()
    
    # Cria o menu de seleção
    prof_selecionado_nome = st.selectbox(
        "Selecione um professor:", 
        options=lista_professores['nome_completo']
    )
    
    # Pega o ID do professor que foi selecionado
    professor_id_para_exibir = int(lista_professores[lista_professores['nome_completo'] == prof_selecionado_nome]['id_usuario'].iloc[0])
    nome_professor_para_exibir = prof_selecionado_nome
    st.write(f"Exibindo painel do Prof(a). *{nome_professor_para_exibir}*")

else:
    # Se um Aluno tentar entrar, ele é bloqueado
    st.error("Acesso não autorizado para este painel.")
    st.stop()

# ==========================================================
# O RESTO DO CÓDIGO DO PAINEL
# (Agora ele roda usando o 'professor_id_para_exibir')
# ==========================================================

try:
    # Carrega o restante dos dados
    df_turmas = pd.read_csv(get_csv_path('turmas.csv'))
    df_disciplinas = pd.read_csv(get_csv_path('diciplinas.csv')) 
    df_matriculas = pd.read_csv(get_csv_path('matriculas.csv'))
    df_notas = pd.read_csv(get_csv_path('notas.csv'))
    df_frequencia = pd.read_csv(get_csv_path('frequencia.csv'))
    
    # --- FILTRO PRINCIPAL: SELEÇÃO DE TURMA ---
    
    # Garantir que a comparação seja de tipos iguais (ex: int vs int)
    df_turmas['id_professor'] = df_turmas['id_professor'].astype(int)
    
    # USA O ID CORRETO!
    turmas_professor = df_turmas[df_turmas['id_professor'] == professor_id_para_exibir]
    
    if turmas_professor.empty:
        # A mensagem agora faz sentido para o Coordenador também
        st.warning(f"O(A) Prof(a). {nome_professor_para_exibir} não está alocado(a) em nenhuma turma.")
        st.stop() 
    
    # O resto do código é exatamente o mesmo de antes
    turmas_professor = pd.merge(turmas_professor, df_disciplinas, on='id_disciplina')
    turmas_professor['turma_display'] = turmas_professor['nome_disciplina'] + " (" + turmas_professor['semestre'].astype(str) + ")"

    turma_selecionada_display = st.selectbox(
        "Selecione uma das turmas para gerenciar:",
        turmas_professor['turma_display']
    )
    
    id_turma_selecionada = turmas_professor[turmas_professor['turma_display'] == turma_selecionada_display].iloc[0]['id_turma']
    nome_disciplina_selecionada = turmas_professor[turmas_professor['turma_display'] == turma_selecionada_display].iloc[0]['nome_disciplina']

    st.markdown("---")

    # --- PREPARAÇÃO DOS DADOS DA TURMA SELECIONADA ---
    matriculas_da_turma = df_matriculas[df_matriculas['id_turma'] == id_turma_selecionada]
    alunos_na_turma = pd.merge(matriculas_da_turma, df_usuarios, left_on='id_aluno', right_on='id_usuario')
    notas_da_turma = df_notas[df_notas['id_matricula'].isin(matriculas_da_turma['id_matricula'])]
    frequencia_da_turma = df_frequencia[df_frequencia['id_matricula'].isin(matriculas_da_turma['id_matricula'])]

    # --- ABAS COM AS FUNCIONALIDADES ---
    tab1, tab2, tab3 = st.tabs(["Visão Geral", "Frequência", "Painel de Desempenho"])

    # --- ABA 1: VISÃO GERAL ---
    with tab1:
        st.subheader(f"Resumo da Turma: {nome_disciplina_selecionada}")
        
        n_alunos = len(alunos_na_turma)
        media_turma = notas_da_turma['valor_nota'].mean() if not notas_da_turma.empty else 0.0
        taxa_presenca_turma = ((frequencia_da_turma['status_presenca'] == 'Presente').sum() / len(frequencia_da_turma) * 100) if not frequencia_da_turma.empty else 0.0
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="label">Nº de Alunos</div><div class="value">{n_alunos}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="label">Média da Turma</div><div class="value">{media_turma:.2f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="label">Taxa de Presença</div><div class="value">{taxa_presenca_turma:.1f}%</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        
        st.subheader("Comparativo de Desempenho (P1 vs. P2)")
        notas_p1_p2 = notas_da_turma[notas_da_turma['tipo_avaliacao'].str.strip().str.lower().isin(['p1', 'p2'])]
        
        if len(notas_p1_p2['tipo_avaliacao'].str.strip().str.lower().unique()) > 1:
            media_p1 = notas_p1_p2[notas_p1_p2['tipo_avaliacao'].str.strip().str.lower() == 'p1']['valor_nota'].mean()
            media_p2 = notas_p1_p2[notas_p1_p2['tipo_avaliacao'].str.strip().str.lower() == 'p2']['valor_nota'].mean()
            media_p1 = media_p1 if pd.notna(media_p1) else 0.0
            media_p2 = media_p2 if pd.notna(media_p2) else 0.0

            g1, g2 = st.columns(2)
            with g1:
                fig_gauge_p1 = go.Figure(go.Indicator(
                    mode = "gauge+number", value = media_p1,
                    title = {'text': "Média P1", 'font': {'size': 24}},
                    gauge = {'axis': {'range': [0, 10]}, 'bar': {'color': "#636EFA"}},
                    number={'font': {'size': 40}}
                ))
                fig_gauge_p1.update_layout(height=250, margin=dict(l=10, r=10, t=80, b=10))
                st.plotly_chart(fig_gauge_p1, use_container_width=True)
            with g2:
                fig_gauge_p2 = go.Figure(go.Indicator(
                    mode = "gauge+number", value = media_p2,
                    title = {'text': "Média P2", 'font': {'size': 24}},
                    gauge = {'axis': {'range': [0, 10]}, 'bar': {'color': "#00CC96"}},
                    number={'font': {'size': 40}}
                ))
                fig_gauge_p2.update_layout(height=250, margin=dict(l=10, r=10, t=80, b=10))
                st.plotly_chart(fig_gauge_p2, use_container_width=True)
        else:
            st.info("O comparativo P1 vs P2 estará disponível quando ambas as notas forem lançadas.")

        st.markdown("---")

        st.subheader("Ranking de Alunos")
        if not notas_da_turma.empty:
            media_por_aluno = pd.merge(
                notas_da_turma.groupby('id_matricula')['valor_nota'].mean().reset_index(), 
                alunos_na_turma[['id_matricula', 'nome_completo']], 
                on='id_matricula'
            )
            media_por_aluno = media_por_aluno.sort_values('valor_nota', ascending=False)
            
            media_por_aluno_display = media_por_aluno.rename(columns={'valor_nota': 'Média', 'nome_completo': 'Aluno'})
            
            r1, r2 = st.columns(2)
            with r1:
                st.write("🏆 *Top 5 Alunos (Melhores Médias)*")
                st.dataframe(media_por_aluno_display.head(5), use_container_width=True, hide_index=True, 
                             column_config={"Média": st.column_config.NumberColumn(format="%.2f")})
            with r2:
                st.write("⚠️ *Alunos que Precisam de Atenção*")
                st.dataframe(media_por_aluno_display.tail(5).sort_values('Média', ascending=True), use_container_width=True, hide_index=True, 
                             column_config={"Média": st.column_config.NumberColumn(format="%.2f")})
        else:
            st.info("As análises de ranking estarão disponíveis após o lançamento de notas.")
        
        st.markdown("---")
        
        st.subheader("Perfil Rápido do Aluno")
        if not alunos_na_turma.empty:
            aluno_selecionado = st.selectbox("Selecione um aluno para análise individual:", options=sorted(alunos_na_turma['nome_completo'].unique()))
            if aluno_selecionado:
                id_matricula_aluno = alunos_na_turma[alunos_na_turma['nome_completo'] == aluno_selecionado].iloc[0]['id_matricula']
                notas_do_aluno = notas_da_turma[notas_da_turma['id_matricula'] == id_matricula_aluno]
                media_aluno = notas_do_aluno['valor_nota'].mean() if not notas_do_aluno.empty else 0.0
                
                col_perfil1, col_perfil2 = st.columns(2)
                with col_perfil1:
                    fig_gauge_aluno = go.Figure(go.Indicator(
                        mode = "gauge+number", value = media_aluno,
                        title = {'text': f"Média de {aluno_selecionado.split()[0]}", 'font': {'size': 24}},
                        gauge = {'axis': {'range': [0, 10]}, 'bar': {'color': "#00CC96"}},
                        number={'font': {'size': 40}}
                    ))
                    fig_gauge_aluno.update_layout(height=250, margin=dict(l=10, r=10, t=80, b=10))
                    st.plotly_chart(fig_gauge_aluno, use_container_width=True)
                with col_perfil2:
                    fig_gauge_turma = go.Figure(go.Indicator(
                        mode = "gauge+number", value = media_turma,
                        title = {'text': "Média da Turma", 'font': {'size': 24}},
                        gauge = {'axis': {'range': [0, 10]}, 'bar': {'color': "lightgray"}},
                        number={'font': {'size': 40}}
                    ))
                    fig_gauge_turma.update_layout(height=250, margin=dict(l=10, r=10, t=80, b=10))
                    st.plotly_chart(fig_gauge_turma, use_container_width=True)
        else:
            st.info("Nenhum aluno matriculado nesta turma para exibir o perfil.")
    
    # --- ABA 2: GESTOR DE FREQUÊNCIA ---
    with tab2:
        st.header("Gestão de Frequência")
        st.write("Esta seção ainda está em desenvolvimento.")
        st.info("Aqui você poderá lançar e editar as frequências dos alunos para esta turma.")
        # ...

    # --- ABA 3: PAINEL DE DESEMPENHO ---
    with tab3:
        st.header("Gestão de Notas (Desempenho)")
        st.write("Esta seção ainda está em desenvolvimento.")
        st.info("Aqui você poderá lançar e editar as notas (P1, P2, Trabalhos) dos alunos.")
        # ...

except FileNotFoundError as e:
    st.error(f"Arquivo de dados não encontrado: {e.filename}. Verifique se o caminho e o nome do arquivo estão corretos e se o script 'gerar_dados_COMPLETOS.py' foi executado.")
except KeyError as e:
    st.error(f"Erro de Coluna: Uma coluna esperada não foi encontrada: {e}. Verifique se os seus CSVs têm todas as colunas necessárias.")
except Exception as e:
    st.error(f"Ocorreu um erro ao processar os dados: {e}")