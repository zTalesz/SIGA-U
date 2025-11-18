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
from datetime import date, datetime
from auth_utils import show_custom_menu
from config import get_csv_path

# --- Configuração da Página ---
# CORREÇÃO: st.set_page_config() deve ser o primeiro comando Streamlit
st.set_page_config(layout="wide")

# --- Autenticação e Menu ---
show_custom_menu()

# Define o nome do arquivo CSV
ATIVIDADES_CSV = get_csv_path('atividades.csv')
HEADERS_CSV = ['id_atividade', 'id_turma', 'titulo', 'descricao', 'data_entrega']

# ==========================================================
# 1. FUNÇÕES DE INFRAESTRUTURA (CSV)
# ==========================================================

def get_todas_atividades():
    """Recupera todas as atividades do arquivo CSV."""
    try:
        df = pd.read_csv(ATIVIDADES_CSV)
        # Força a coluna id_atividade a ser do tipo int
        if 'id_atividade' in df.columns:
             df['id_atividade'] = df['id_atividade'].astype(int)
        if df.empty and list(df.columns) != HEADERS_CSV:
             return pd.DataFrame(columns=HEADERS_CSV)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        if not os.path.exists(ATIVIDADES_CSV):
            pd.DataFrame(columns=HEADERS_CSV).to_csv(ATIVIDADES_CSV, index=False)
        return pd.DataFrame(columns=HEADERS_CSV)

def adicionar_atividade(id_turma, titulo, data_entrega_dt, descricao=""):
    """Adiciona a atividade ao CSV."""
    df = get_todas_atividades()
    if df.empty or 'id_atividade' not in df.columns or df['id_atividade'].max() != df['id_atividade'].max(): # Checa se está vazio ou tem NaN
        new_id = 1
    else:
        new_id = int(df['id_atividade'].max()) + 1
        
    data_entrega_str = data_entrega_dt.isoformat()
    nova_atividade = {
        'id_atividade': new_id,
        'id_turma': id_turma,
        'titulo': titulo,
        'descricao': descricao,
        'data_entrega': data_entrega_str
    }
    df_nova = pd.DataFrame([nova_atividade])
    df_final = pd.concat([df, df_nova], ignore_index=True)
    
    try:
        df_final.to_csv(ATIVIDADES_CSV, index=False)
        return f"SUCESSO! Atividade '{titulo}' adicionada."
    except Exception as e:
        return f"Ocorreu um erro ao salvar o CSV: {e}"

# NOVO: Função para editar uma atividade existente
def editar_atividade(atividade_id, novo_id_turma, novo_titulo, nova_data_entrega_dt, nova_descricao):
    """Edita uma atividade existente no CSV."""
    df = get_todas_atividades()
    
    if 'id_atividade' not in df.columns or atividade_id not in df['id_atividade'].values:
        return f"ERRO: Nenhuma atividade encontrada com o ID {atividade_id}."

    # Encontrar o índice da linha a ser editada
    try:
        # Garante que o ID é do tipo int para comparação
        df['id_atividade'] = df['id_atividade'].astype(int)
        index_atividade = df[df['id_atividade'] == atividade_id].index[0]
    except IndexError:
         return f"ERRO: Índice não encontrado para o ID {atividade_id}."
    except Exception as e:
        return f"ERRO ao localizar atividade: {e}"

    # Converter a data para string ISO
    nova_data_entrega_str = nova_data_entrega_dt.isoformat()

    # Atualizar os valores na linha encontrada
    df.loc[index_atividade, 'id_turma'] = novo_id_turma
    df.loc[index_atividade, 'titulo'] = novo_titulo
    df.loc[index_atividade, 'data_entrega'] = nova_data_entrega_str
    df.loc[index_atividade, 'descricao'] = nova_descricao
    
    try:
        df.to_csv(ATIVIDADES_CSV, index=False)
        return f"SUCESSO! Atividade '{novo_titulo}' (ID {atividade_id}) foi atualizada."
    except Exception as e:
        return f"Ocorreu um erro ao salvar o CSV após editar: {e}"
# FIM DA NOVA FUNÇÃO

def deletar_atividade(atividade_id):
    """Deleta uma atividade do CSV usando o seu ID."""
    df = get_todas_atividades()
    
    # Garante que o ID é do tipo int para comparação
    atividade_id = int(atividade_id)
    
    if 'id_atividade' not in df.columns or atividade_id not in df['id_atividade'].values:
        return f"ERRO: Nenhuma atividade encontrada com o ID {atividade_id}."
        
    df_filtrado = df[df['id_atividade'] != atividade_id]
    
    try:
        df_filtrado.to_csv(ATIVIDADES_CSV, index=False)
        return f"SUCESSO! Atividade com ID {atividade_id} foi deletada."
    except Exception as e:
        return f"Ocorreu um erro ao salvar o CSV após deletar: {e}"

# ==========================================================
# 2. INTERFACE STREAMLIT
# ==========================================================

def menu_professor_streamlit():
    st.title("👨‍🏫 Plataforma de Gerenciamento de Prazos")
    st.caption("Visão do Professor: Publicação, Edição e Exclusão de Atividades.")

    # Carregar dados relacionais
    try:
        professor_id = st.session_state.user_info['id_usuario']
        # MODIFICADO: Corrigindo o caminho dos arquivos CSV para usar a função de config
        # Isso torna o código mais robusto e portátil
        df_turmas = pd.read_csv(get_csv_path('turmas.csv'))
        df_disciplinas = pd.read_csv(get_csv_path('diciplinas.csv')) 
    except Exception as e:
        st.error(f"Não foi possível carregar os dados das turmas: {e}")
        return

    # Filtrar turmas do professor logado
    turmas_professor = df_turmas[df_turmas['id_professor'] == professor_id]
    turmas_professor = pd.merge(turmas_professor, df_disciplinas, on='id_disciplina')
    turmas_professor['turma_display'] = turmas_professor['nome_disciplina'] + " (" + turmas_professor['semestre'].astype(str) + ")"
    
    if turmas_professor.empty:
        st.warning("Você não está alocado em nenhuma turma e não pode publicar atividades.")
        return

    # Recupera todas as atividades
    df_atividades_todas = get_todas_atividades()
    
    # Junta atividades com as turmas do professor para exibir
    if not df_atividades_todas.empty and 'id_turma' in df_atividades_todas.columns:
        # Garante que os IDs para o merge são do mesmo tipo (int)
        df_atividades_todas['id_turma'] = df_atividades_todas['id_turma'].astype(int)
        turmas_professor['id_turma'] = turmas_professor['id_turma'].astype(int)
        
        df_atividades_visivel = pd.merge(df_atividades_todas, turmas_professor, on='id_turma', how="inner")
    else:
        # Cria DF vazio com colunas
        df_atividades_visivel = pd.DataFrame(columns=HEADERS_CSV + ['turma_display', 'nome_disciplina']) 
        
    st.markdown("---")
    
    # MODIFICADO: Adicionada a nova "tab_editar"
    tab_ver, tab_publicar, tab_editar, tab_deletar = st.tabs([
        "Visualizar Prazos", 
        "Publicar Nova Atividade", 
        "✏️ Editar Atividade", 
        "Deletar Atividade"
    ])

    # --- ABA DE VISUALIZAÇÃO ---
    with tab_ver:
        st.subheader("📋 Atividades Publicadas por Você")
        if df_atividades_visivel.empty:
            st.warning("Nenhuma atividade encontrada para suas turmas. Publique a primeira!")
        else:
            # Garante que 'id_atividade' existe antes de renomear
            if 'id_atividade' in df_atividades_visivel.columns:
                df_exibicao = df_atividades_visivel.rename(columns={
                    'id_atividade': 'ID',
                    'turma_display': 'Turma',
                    'titulo': 'Título',
                    'data_entrega': 'Prazo',
                    'descricao': 'Detalhes'
                })
                st.dataframe(df_exibicao[['ID', 'Turma', 'Título', 'Prazo', 'Detalhes']], use_container_width=True, hide_index=True)
            else:
                st.error("Erro ao processar colunas de atividades.")


    # --- ABA DE PUBLICAÇÃO ---
    with tab_publicar:
        st.subheader("📝 Publicar Nova Atividade")
        with st.form("form_publicacao", clear_on_submit=True):
            turma_selecionada_display = st.selectbox("Selecione a Turma:", options=turmas_professor['turma_display'], key="sb_publicar")
            titulo = st.text_input("Título da Atividade:")
            data_entrega = st.date_input("Data de Entrega:", min_value=date.today(), value=date.today())
            descricao = st.text_area("Descrição Detalhada (Opcional):", height=100)
            publicar_button = st.form_submit_button("Publicar no Calendário")
            
            if publicar_button:
                if not titulo or not turma_selecionada_display:
                    st.error("Título e Turma são obrigatórios!")
                else:
                    id_turma_selecionada = turmas_professor[turmas_professor['turma_display'] == turma_selecionada_display].iloc[0]['id_turma']
                    resultado = adicionar_atividade(id_turma_selecionada, titulo, data_entrega, descricao)
                    if "SUCESSO" in resultado:
                        st.success(resultado)
                        st.rerun() # Adicionado rerun para atualizar a visualização
                    else:
                        st.error(resultado)

    # NOVO: Bloco inteiro para a aba de Edição
    with tab_editar:
        st.subheader("✏️ Editar Atividade Existente")
        if df_atividades_visivel.empty:
            st.info("Nenhuma atividade publicada por você para ser editada.")
        else:
            # 1. Selecionar a atividade (igual ao de deletar)
            df_atividades_visivel['id_atividade'] = df_atividades_visivel['id_atividade'].astype(int)
            opcoes_edicao = [f"{row['id_atividade']} - {row['titulo']} (Turma: {row['turma_display']})" 
                              for index, row in df_atividades_visivel.iterrows()]
            selecao_edicao = st.selectbox("Selecione a atividade para editar:", options=opcoes_edicao, key="sb_editar")
            
            if selecao_edicao:
                # 2. Extrair dados da atividade selecionada
                id_para_editar = int(selecao_edicao.split(' - ')[0])
                # Pegar a linha inteira da atividade
                atividade_atual = df_atividades_visivel[df_atividades_visivel['id_atividade'] == id_para_editar].iloc[0]

                # 3. Preencher o formulário com dados atuais
                with st.form("form_edicao"):
                    st.info(f"Editando Atividade ID: {id_para_editar}")

                    # Obter índice da turma atual para o selectbox
                    lista_turmas_display = list(turmas_professor['turma_display'])
                    try:
                        indice_turma_atual = lista_turmas_display.index(atividade_atual['turma_display'])
                    except ValueError:
                        indice_turma_atual = 0 # Caso seguro se a turma não for encontrada

                    # Campos do formulário
                    turma_selecionada_display_edit = st.selectbox(
                        "Selecione a Turma:", 
                        options=lista_turmas_display, 
                        index=indice_turma_atual,
                        key="sb_edit_turma"
                    )
                    
                    titulo_edit = st.text_input(
                        "Título da Atividade:", 
                        value=atividade_atual['titulo']
                    )
                    
                    # Converter data_entrega de string para objeto date
                    try:
                        data_entrega_atual = datetime.fromisoformat(atividade_atual['data_entrega']).date()
                    except ValueError:
                        data_entrega_atual = date.today() # Fallback

                    data_entrega_edit = st.date_input(
                        "Data de Entrega:", 
                        min_value=date.today(), 
                        value=data_entrega_atual
                    )
                    
                    descricao_edit = st.text_area(
                        "Descrição Detalhada (Opcional):", 
                        value=atividade_atual['descricao'], 
                        height=100
                    )
                    
                    editar_button = st.form_submit_button("Salvar Alterações")
                    
                    if editar_button:
                        if not titulo_edit or not turma_selecionada_display_edit:
                            st.error("Título e Turma são obrigatórios!")
                        else:
                            # 4. Obter dados do form e chamar a função
                            id_turma_nova = turmas_professor[turmas_professor['turma_display'] == turma_selecionada_display_edit].iloc[0]['id_turma']
                            
                            resultado = editar_atividade(
                                atividade_id=id_para_editar,
                                novo_id_turma=id_turma_nova,
                                novo_titulo=titulo_edit,
                                nova_data_entrega_dt=data_entrega_edit,
                                nova_descricao=descricao_edit
                            )
                            
                            if "SUCESSO" in resultado:
                                st.success(resultado)
                                st.rerun() # Recarrega a página para atualizar as listas
                            else:
                                st.error(resultado)
            else:
                 st.info("Nenhuma atividade selecionada para edição.")
    # FIM DO NOVO BLOCO

    # --- ABA DE DELEÇÃO ---
    with tab_deletar:
        st.subheader("🗑️ Deletar Atividade")
        if df_atividades_visivel.empty:
            st.info("Nenhuma atividade publicada por você para ser deletada.")
        else:
            df_atividades_visivel['id_atividade'] = df_atividades_visivel['id_atividade'].astype(int)
            opcoes_delecao = [f"{row['id_atividade']} - {row['titulo']} (Turma: {row['turma_display']})" 
                              for index, row in df_atividades_visivel.iterrows()]
            selecao = st.selectbox("Selecione a atividade para deletar:", options=opcoes_delecao, key="sb_deletar")
            
            # Garante que há uma seleção antes de tentar extrair o ID
            if selecao: 
                id_para_deletar = int(selecao.split(' - ')[0])
                if st.button(f"Confirmar Deleção do ID {id_para_deletar}", type="primary"):
                    resultado = deletar_atividade(id_para_deletar)
                    if "SUCESSO" in resultado:
                        st.success(resultado)
                        st.rerun() 
                    else:
                        st.error(resultado)
            else:
                 st.info("Nenhuma atividade selecionada para deleção.")


# --- Iniciar a Aplicação ---
menu_professor_streamlit()