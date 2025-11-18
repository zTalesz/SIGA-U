# Bloco de código para o topo de CADA ARQUIVO EM 'pages/'
import sys
import os
import streamlit as st

pages_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(pages_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
# Fim do bloco

import pandas as pd
from datetime import date
from auth_utils import show_custom_menu
from config import get_csv_path

# --- Configuração da Página ---
st.set_page_config(layout="wide")

# --- Autenticação e Menu ---
show_custom_menu()

# --- CONSTANTES ---
RECADOS_CSV = get_csv_path('recados.csv')

# ==========================================================
# FUNÇÃO DE CONSULTA
# ==========================================================

def get_recados_aluno(aluno_id):
    """
    Recupera os recados destinados ao aluno.
    - Recados "Geral"
    - Recados da(s) turma(s) do aluno
    Retorna um DataFrame processado ou None em caso de erro.
    """
    try:
        # 1. Carregar todos os dados necessários
        df_recados = pd.read_csv(RECADOS_CSV)
        df_matriculas = pd.read_csv(get_csv_path('matriculas.csv'))

        if df_recados.empty:
            return pd.DataFrame()

        # 2. Encontrar as turmas do aluno
        turmas_do_aluno = df_matriculas[df_matriculas['id_aluno'] == aluno_id]['id_turma'].unique()
        
        # Converter IDs para string para comparação (pois 'publico_alvo_turma_id' pode ser 'Geral')
        turmas_do_aluno_str = [str(t) for t in turmas_do_aluno]
        df_recados['publico_alvo_turma_id'] = df_recados['publico_alvo_turma_id'].astype(str)

        # 3. Filtrar recados
        # Filtro 1: Recados para "Geral"
        filtro_geral = df_recados['publico_alvo_turma_id'] == 'Geral'
        
        # Filtro 2: Recados para as turmas específicas do aluno
        filtro_turma = df_recados['publico_alvo_turma_id'].isin(turmas_do_aluno_str)
        
        # Combina os filtros ( | significa OU )
        df_recados_aluno = df_recados[filtro_geral | filtro_turma]

        if df_recados_aluno.empty:
            return pd.DataFrame()

        # 4. Ordenar por data (mais recentes primeiro)
        df_recados_aluno = df_recados_aluno.sort_values(by='data_publicacao', ascending=False)
        return df_recados_aluno
        
    except (FileNotFoundError, pd.errors.EmptyDataError):
        st.error(f"ERRO: O arquivo de recados ('recados.csv') não foi encontrado.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao acessar os dados: {e}")
        return None

# ==========================================================
# FUNÇÃO PRINCIPAL DE EXIBIÇÃO
# ==========================================================

def exibir_mural_aluno():
    st.title("📌 Mural de Recados")
    st.markdown("Veja aqui os comunicados da coordenação e dos seus professores.")
    
    aluno_id = st.session_state.user_info['id_usuario']
    df_recados = get_recados_aluno(aluno_id)
    
    if df_recados is None:
        return # Erro já foi mostrado pela função

    if df_recados.empty:
        st.info("Nenhum recado no mural para você no momento.")
        return

    st.markdown("---")
    
    # Define colunas para o layout (estilo "varal")
    # Altere o número 3 para mais ou menos colunas de recados
    cols = st.columns(3) 
    
    # Itera e distribui os recados nas colunas
    for i, (_, row) in enumerate(df_recados.iterrows()):
        col = cols[i % len(cols)] # Distribui entre as colunas
        
        # Usamos st.container(border=True) para criar o "post-it"
        with col:
            with st.container(border=True):
                st.subheader(f" {row['titulo']}")
                st.markdown(row['mensagem'])
                st.markdown("---")
                st.caption(f"De: {row['autor_nome']} | Em: {row['data_publicacao']}")

# --- Iniciar a Aplicação ---
exibir_mural_aluno()