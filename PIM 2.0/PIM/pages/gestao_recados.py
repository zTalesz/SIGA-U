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
# Você pediu um script em 'scripts/', mas seu código 'gestao_prazos_professor.py' 
# já usa um método melhor: criar o CSV se ele não existir. Vamos usar esse método.
RECADOS_CSV = get_csv_path('recados.csv')
HEADERS_CSV = ['id_recado', 'titulo', 'mensagem', 'autor_nome', 'autor_id', 'data_publicacao', 'publico_alvo_turma_id']

# ==========================================================
# 1. FUNÇÕES DE INFRAESTRUTURA (CSV)
# ==========================================================

def get_todos_recados():
    """Recupera todos os recados do arquivo CSV."""
    try:
        df = pd.read_csv(RECADOS_CSV)
        if df.empty and list(df.columns) != HEADERS_CSV:
             return pd.DataFrame(columns=HEADERS_CSV)
        # Garante que colunas de ID sejam string para consistência
        df['autor_id'] = df['autor_id'].astype(str)
        df['id_recado'] = df['id_recado'].astype(int)
        df['publico_alvo_turma_id'] = df['publico_alvo_turma_id'].astype(str)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        if not os.path.exists(RECADOS_CSV):
            pd.DataFrame(columns=HEADERS_CSV).to_csv(RECADOS_CSV, index=False)
        return pd.DataFrame(columns=HEADERS_CSV)

def adicionar_recado(titulo, mensagem, publico_alvo_turma_id, autor_info):
    """Adiciona um novo recado ao CSV."""
    df = get_todos_recados()
    
    if df.empty or 'id_recado' not in df.columns or df['id_recado'].max() != df['id_recado'].max(): # Checa se está vazio ou tem NaN
        new_id = 1
    else:
        new_id = int(df['id_recado'].max()) + 1
        
    novo_recado = {
        'id_recado': new_id,
        'titulo': titulo,
        'mensagem': mensagem,
        'autor_nome': autor_info['nome_completo'],
        'autor_id': str(autor_info['id_usuario']),
        'data_publicacao': date.today().isoformat(),
        'publico_alvo_turma_id': str(publico_alvo_turma_id) # 'Geral' ou ID da turma
    }
    df_nova = pd.DataFrame([novo_recado])
    df_final = pd.concat([df, df_nova], ignore_index=True)
    
    try:
        df_final.to_csv(RECADOS_CSV, index=False)
        return f"SUCESSO! Recado '{titulo}' publicado no mural."
    except Exception as e:
        return f"Ocorreu um erro ao salvar o CSV: {e}"

def deletar_recado(recado_id):
    """Deleta um recado do CSV usando o seu ID."""
    df = get_todos_recados()
    
    recado_id = int(recado_id)
    if 'id_recado' not in df.columns or recado_id not in df['id_recado'].values:
        return f"ERRO: Nenhum recado encontrado com o ID {recado_id}."
        
    df_filtrado = df[df['id_recado'] != recado_id]
    
    try:
        df_filtrado.to_csv(RECADOS_CSV, index=False)
        return f"SUCESSO! Recado com ID {recado_id} foi removido."
    except Exception as e:
        return f"Ocorreu um erro ao salvar o CSV após deletar: {e}"

# ==========================================================
# 2. INTERFACE STREAMLIT
# ==========================================================

def menu_gestao_recados():
    st.title("📌 Gerenciador de Recados do Mural")
    
    # Informações do usuário logado
    user_info = st.session_state.user_info
    user_role = user_info['role']
    user_id = str(user_info['id_usuario'])

    # Carregar dados das turmas para o selectbox
    try:
        df_turmas = pd.read_csv(get_csv_path('turmas.csv'))
        df_disciplinas = pd.read_csv(get_csv_path('diciplinas.csv')) 
        turmas_com_disciplinas = pd.merge(df_turmas, df_disciplinas, on='id_disciplina')
        turmas_com_disciplinas['turma_display'] = turmas_com_disciplinas['nome_disciplina'] + " - Semestre: " + turmas_com_disciplinas['semestre'].astype(str)
        # Opções de público-alvo: Começa com "Geral" e depois adiciona as turmas
        opcoes_publico = {"Geral": "Geral"}
        opcoes_publico.update({row['turma_display']: str(row['id_turma']) for _, row in turmas_com_disciplinas.iterrows()})
        
    except Exception as e:
        st.error(f"Não foi possível carregar os dados das turmas: {e}")
        return

    # Recupera todos os recados
    df_recados_todos = get_todos_recados()
    
    st.markdown("---")
    
    tab_publicar, tab_deletar = st.tabs([
        "Publicar Novo Recado", 
        "Deletar Recados"
    ])

    # --- ABA DE PUBLICAÇÃO ---
    with tab_publicar:
        st.subheader("📝 Publicar Novo Recado")
        with st.form("form_publicacao", clear_on_submit=True):
            
            titulo = st.text_input("Título do Recado:")
            mensagem = st.text_area("Mensagem:", height=150)
            
            # Selectbox para escolher o público-alvo
            publico_selecionado_display = st.selectbox(
                "Publicar para:", 
                options=opcoes_publico.keys() # Mostra os nomes amigáveis (ex: "Geral", "Matemática - Semestre 1")
            )
            
            publicar_button = st.form_submit_button("Publicar no Mural")
            
            if publicar_button:
                if not titulo or not mensagem:
                    st.error("Título e Mensagem são obrigatórios!")
                else:
                    # Pega o ID correspondente ao nome amigável (ex: "Geral" -> "Geral", "Matemática..." -> "5")
                    publico_alvo_id = opcoes_publico[publico_selecionado_display]
                    
                    resultado = adicionar_recado(titulo, mensagem, publico_alvo_id, user_info)
                    
                    if "SUCESSO" in resultado:
                        st.success(resultado)
                        st.rerun()
                    else:
                        st.error(resultado)

    # --- ABA DE DELEÇÃO ---
    with tab_deletar:
        st.subheader("🗑️ Deletar Recados")
        
        # Lógica de Permissão:
        # Professor: só vê/deleta seus próprios recados.
        # Coordenação/Admin: vê/deleta TODOS os recados.
        
        if user_role in ['Coordenação', 'Administração']:
            st.info("Perfil de Administrador: visualizando todos os recados do mural.")
            df_recados_visiveis = df_recados_todos
        else: # Professor
            st.info("Perfil de Professor: visualizando apenas os recados criados por você.")
            df_recados_visiveis = df_recados_todos[df_recados_todos['autor_id'] == user_id]

        if df_recados_visiveis.empty:
            st.warning("Nenhum recado encontrado para deletar.")
        else:
            # Criar opções amigáveis para o selectbox
            opcoes_delecao = [
                f"{row['id_recado']} - {row['titulo']} (Autor: {row['autor_nome']}, Data: {row['data_publicacao']})" 
                for _, row in df_recados_visiveis.iterrows()
            ]
            
            selecao = st.selectbox("Selecione o recado para deletar:", options=opcoes_delecao, key="sb_deletar")
            
            if selecao:
                id_para_deletar = int(selecao.split(' - ')[0])
                
                if st.button(f"Confirmar Deleção do ID {id_para_deletar}", type="primary"):
                    resultado = deletar_recado(id_para_deletar)
                    if "SUCESSO" in resultado:
                        st.success(resultado)
                        st.rerun()
                    else:
                        st.error(resultado)

# --- Iniciar a Aplicação ---
menu_gestao_recados()