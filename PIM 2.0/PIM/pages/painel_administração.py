# --- Configuração de Path ---
import sys
import os
import streamlit as st 
# --- Imports (DEPOIS da configuração de path) ---
import pandas as pd
from datetime import datetime
from scripts.utils import *
# CORREÇÃO: Importa da pasta 'scripts'
from auth_utils import *

# Pega o diretório do script atual (pages/painel_administracao.py)
try:
    current_script_path = os.path.abspath(__file__)
    pages_dir = os.path.dirname(current_script_path)
    project_root = os.path.dirname(pages_dir)
except NameError:
    st.error("Falha ao determinar o diretório do projeto. Faça login novamente.")
    st.stop()


# Adiciona a raiz do projeto ao sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

# Muda o diretório de trabalho atual para a raiz do projeto
try:
    os.chdir(project_root)
except FileNotFoundError:
    st.error(f"Não foi possível encontrar o diretório do projeto: {project_root}")
    st.stop()
# --- Fim da Configuração de Path ---





# --- Verificação de Autenticação ---
if not st.session_state.get('logged_in', False):
    st.error("Você precisa estar logado para acessar esta página.")
    st.switch_page("main.py") 
    st.stop() 

user_info = st.session_state.get('user_info', {})
if user_info.get('role') != 'Administração':
    st.error("Acesso negado. Esta página é restrita a administradores.")
    show_custom_menu() 
    st.stop() 
# --- Fim da Verificação ---


def admin_panel():
    """
    Interface principal do Administrador.
    """

    # --- Carregamento Único e Verificação de Cursos ---
    # CSV: id_curso,nome_curso
    df_cursos = load_cursos() 
    
    cursos_validos = (
        not df_cursos.empty and 
        "nome_curso" in df_cursos.columns and 
        "id_curso" in df_cursos.columns
    )

    if cursos_validos:
        lista_cursos_nomes = df_cursos['nome_curso'].tolist()
    else:
        st.error(
            "Erro Crítico: Arquivo 'cursos.csv' não foi carregado ou está inválido. "
            "As colunas 'nome_curso' e 'id_curso' são obrigatórias. "
            "Muitas funções do painel de ADM ficarão desativadas."
        )
        lista_cursos_nomes = []
        df_cursos = pd.DataFrame(columns=["id_curso", "nome_curso"])

    
    # === Ajuste de compatibilidade com a nova estrutura ===
    info = st.session_state.user_info
    if "user" not in st.session_state:
        st.session_state.user = {
            # O 'id' do nosso sistema será o 'username' do CSV
            "id": info.get("username"), 
            "nome": info.get("nome_completo"),
            "role": info.get("role")
        }
    
    if st.session_state.user.get("id") is None: st.session_state.user['id'] = "ADM_ERR"
    if st.session_state.user.get("nome") is None: st.session_state.user['nome'] = "Admin (Erro)"
    # === Fim do Ajuste de compatibilidade ===


    st.title("Painel do Administrador")
    st.sidebar.markdown(f"*Logado como:* {st.session_state.user['nome']} ({st.session_state.user['id']})")
    tab = st.sidebar.radio("Ações", ["Dashboard", "Gerenciar Usuários", "Criar Usuário", "Turmas", "Sair"])

    # ----------------- Aba: Sair -----------------
    if tab == "Sair":
        if st.button("Logout"):
            logout() 
        return

    # ----------------- Aba: Dashboard -----------------
    if tab == "Dashboard":
        st.subheader("Visão Geral do Sistema")
        df = load_users()
        if df.empty:
            st.warning("Nenhum usuário encontrado. Crie um usuário na aba 'Criar Usuário'.")
            return

        # Bloco de compatibilidade
        # CSV: username, nome_completo, role
        if "id" not in df.columns and "username" in df.columns:
            df = df.rename(columns={"username": "id"})
        if "nome" not in df.columns and "nome_completo" in df.columns:
             df = df.rename(columns={"nome_completo": "nome"})
        if "status" not in df.columns: 
            df["status"] = "ativo" # Assume 'ativo' se a coluna não existir

        st.metric("Total de usuários", len(df))
        st.metric("Professores pendentes", len(df[(df["role"] == "Professor") & (df["status"] == "pendente")]))
        
        st.dataframe(df[["id", "nome", "role", "status"]], use_container_width=True)


    # ----------------- Aba: Gerenciar Usuários -----------------
    if tab == "Gerenciar Usuários":
        st.subheader("Listar / Editar / Excluir Usuários")

        df_display = load_users()
        if df_display.empty:
            st.warning("Nenhum usuário encontrado. Crie um usuário na aba 'Criar Usuário'.")
            return

        # Bloco de compatibilidade
        # CSV: username, nome_completo, role, status, id_curso
        if "id" not in df_display.columns and "username" in df_display.columns:
            df_display = df_display.rename(columns={"username": "id"})
        if "nome" not in df_display.columns and "nome_completo" in df_display.columns:
             df_display = df_display.rename(columns={"nome_completo": "nome"})
        if "status" not in df_display.columns: 
            df_display["status"] = "ativo"
        # Garante que a coluna 'id_curso' (de usuarios.csv) exista
        if "id_curso" not in df_display.columns:
            df_display["id_curso"] = "" 

        if cursos_validos:
            df_display = pd.merge(
                df_display, 
                df_cursos, 
                left_on='id_curso', # Coluna em usuarios.csv
                right_on='id_curso',# Coluna em cursos.csv
                how='left'
            )
            df_display['Curso'] = df_display['nome_curso'].fillna(df_display['id_curso'])
        else:
            df_display['Curso'] = df_display.get('id_curso', '')


        colunas_visiveis = [c for c in ["id", "nome", "role", "Curso", "status"] if c in df_display.columns]
        st.dataframe(df_display[colunas_visiveis], use_container_width=True)

        st.markdown("---")
        st.markdown("*Aprovar Professores Pendentes*")

        pendentes = df_display[(df_display["role"] == "Professor") & (df_display["status"] == "pendente")]
        if not pendentes.empty:
            sel = st.selectbox("Professor pendente", pendentes["id"] + " — " + pendentes["nome"])
            if st.button("Aprovar selecionado"):
                pid = sel.split(" — ")[0]
                df_original_users = load_users() 
                
                # Encontra o usuário pelo 'username'
                df_original_users.loc[df_original_users["username"] == pid, "status"] = "ativo"
                save_users(df_original_users)
                st.success(f"{pid} aprovado.")
                st.rerun()
        else:
            st.info("Sem professores pendentes.")

        st.markdown("---")
        st.markdown("*Editar / Excluir Usuário*")
        
        df_original_users = load_users()
        # Usa 'username' como a chave 'id' interna
        if "id" not in df_original_users.columns and "username" in df_original_users.columns:
            df_original_users = df_original_users.rename(columns={"username": "id"})

        all_ids = df_original_users["id"].tolist()
        chosen = st.selectbox("Selecione usuário", ["--"] + all_ids)
        
        if chosen and chosen != "--":
            user_row = df_original_users[df_original_users["id"] == chosen].iloc[0].to_dict()
            
            with st.form("edit_user"):
                nome_atual = user_row.get("nome", user_row.get("nome_completo", ""))
                new_name = st.text_input("Nome", value=nome_atual)
                
                status_options = ["ativo", "pendente", "inativo"]
                current_status = user_row.get("status", "ativo")
                current_index = status_options.index(current_status) if current_status in status_options else 0
                new_status = st.selectbox("Status", status_options, index=current_index)
                
                user_role = user_row.get("role")
                if user_role == "Aluno":
                    current_id_curso = user_row.get("id_curso", "")
                    current_nome_curso = ""
                    
                    if current_id_curso and cursos_validos:
                        curso_match = df_cursos[df_cursos['id_curso'] == current_id_curso]
                        if not curso_match.empty:
                            current_nome_curso = curso_match.iloc[0]['nome_curso']
                    
                    current_curso_index = 0
                    if current_nome_curso in lista_cursos_nomes:
                        current_curso_index = lista_cursos_nomes.index(current_nome_curso) + 1 
                    
                    new_curso_nome = st.selectbox("Curso", ["--"] + lista_cursos_nomes, index=current_curso_index, disabled=not cursos_validos)
                    
                elif user_role == "Professor":
                     new_course_disc = st.text_input("Disciplina Principal", value=user_row.get("id_curso", ""))
                
                submit_edit = st.form_submit_button("Salvar alterações")

                if submit_edit:
                    df_original_users.loc[df_original_users["id"] == chosen, "nome_completo"] = new_name
                    if "nome" in df_original_users.columns:
                        df_original_users.loc[df_original_users["id"] == chosen, "nome"] = new_name
                    
                    if "status" not in df_original_users.columns:
                        df_original_users["status"] = "ativo"
                    df_original_users.loc[df_original_users["id"] == chosen, "status"] = new_status
                    
                    if "id_curso" not in df_original_users.columns:
                        df_original_users["id_curso"] = ""
                        
                    if user_role == "Aluno":
                        if new_curso_nome != "--" and cursos_validos:
                            novo_id_curso = df_cursos.loc[df_cursos['nome_curso'] == new_curso_nome, 'id_curso'].iloc[0]
                            df_original_users.loc[df_original_users["id"] == chosen, "id_curso"] = novo_id_curso
                        else:
                             df_original_users.loc[df_original_users["id"] == chosen, "id_curso"] = ""
                    elif user_role == "Professor":
                         df_original_users.loc[df_original_users["id"] == chosen, "id_curso"] = new_course_disc

                    save_users(df_original_users)
                    st.success("Alterações salvas.")
                    st.rerun()

            if st.button("Excluir Usuário"):
                df_original_users = df_original_users[df_original_users["id"] != chosen]
                save_users(df_original_users)
                
                matriculas = load_matriculas()
                if not matriculas.empty:
                    # CSV: id_aluno, id_turma
                    if "id_aluno" not in matriculas.columns: matriculas["id_aluno"] = ""
                        
                    matriculas = matriculas[matriculas["id_aluno"] != chosen]
                    save_matriculas(matriculas)
                
                st.success("Usuário e matrículas associadas excluídos.")
                st.rerun()


    # ----------------- Aba: Criar Usuário -----------------
    if tab == "Criar Usuário": 
        st.subheader("Criar Usuário (Administrador, Coordenação, Professor ou Aluno)")

        tipos = ["Administrador", "Coordenação", "Professor", "Aluno"]
        tipo = st.selectbox("Tipo", tipos)

        nome = st.text_input("Nome completo")
        data_nasc = st.date_input(
            "Data de nascimento",
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.now().date()
        )
        cpf = st.text_input("CPF (apenas números)")
        senha = st.text_input("Senha inicial (compartilhar com usuário)", type="password")
        
        # Campos extras do CSV usuarios
        rg = st.text_input("RG")
        campus = st.text_input("Campus", "Tatuapé")
        validade_carteirinha = st.text_input("Validade da Carteirinha", "12/2026")
        path_foto = st.text_input("Caminho da Foto", "fotos/default.jpg")

        curso_nome_selecionado = None
        disciplina_texto = None # Para professores

        if tipo == "Aluno":
            curso_nome_selecionado = st.selectbox("Curso", ["--"] + lista_cursos_nomes, disabled=not cursos_validos)

        elif tipo == "Professor":
            st.selectbox("Curso (área da disciplina)", ["--"] + lista_cursos_nomes, disabled=not cursos_validos)
            disciplina_texto = st.text_input("Disciplina Principal (ex: Lógica de Programação)")

        if st.button("Cadastrar"):
            if not nome or len(senha) < 4:
                st.error("Preencha nome e senha com pelo menos 4 caracteres.")
            elif not validate_cpf(cpf):
                st.error("CPF inválido. Digite apenas números e verifique se está correto.")
            elif tipo == "Aluno" and (not curso_nome_selecionado or curso_nome_selecionado == "--"):
                st.error("Por favor, selecione um curso para o aluno.")
            else:
                df = load_users()
                if 'cpf' not in df.columns: df['cpf'] = pd.Series(dtype='str')
                df['cpf'] = df['cpf'].astype(str).str.replace(r'\.0$', '', regex=True)

                if cpf in df["cpf"].values:
                    st.error("Já existe um usuário cadastrado com esse CPF.")
                else:
                    id_curso_selecionado = ""
                    if curso_nome_selecionado and curso_nome_selecionado != "--" and cursos_validos:
                        try:
                            id_curso_selecionado = df_cursos.loc[df_cursos['nome_curso'] == curso_nome_selecionado, 'id_curso'].iloc[0]
                        except IndexError:
                            id_curso_selecionado = ""
                    
                    # Professores e Alunos usam a coluna 'id_curso'
                    if tipo == "Aluno":
                        curso_disc_final = id_curso_selecionado
                    else:
                        curso_disc_final = disciplina_texto or ""
                    
                    prefixo = {"Aluno": "ALU", "Professor": "PRO", "Coordenação": "COO", "Administrador": "ADM"}.get(tipo, "USR")
                    
                    if 'username' not in df.columns:
                         df['username'] = pd.Series(dtype='str')
                         
                    df['username'] = df['username'].astype(str)
                    ids_com_prefixo = df[df['username'].str.startswith(prefixo, na=False)]['username'].str.replace(prefixo, '')
                    ids_numericos = pd.to_numeric(ids_com_prefixo, errors='coerce').dropna()
                    next_num = 1 if ids_numericos.empty else int(ids_numericos.max()) + 1
                    new_id_str = f"{prefixo}{next_num:03d}"

                    if 'id_usuario' not in df.columns:
                        df['id_usuario'] = pd.to_numeric(df.index, errors='coerce') + 1
                    
                    next_id_usuario = (pd.to_numeric(df['id_usuario'], errors='coerce').max() or 0) + 1

                    # CSV: id_usuario,nome_completo,username,password,role,rg,cpf,id_curso,campus,validade,path_foto
                    row = {
                        "id_usuario": str(next_id_usuario),
                        "nome_completo": nome,
                        "username": new_id_str,
                        "password": senha,
                        "role": tipo,
                        "rg": rg,
                        "cpf": cpf,
                        "id_curso": curso_disc_final, 
                        "campus": campus,
                        "validade": validade_carteirinha,
                        "path_foto": path_foto,
                        # Colunas extras
                        "status": "ativo", 
                        "must_change_password": "False",
                        "date_created": datetime.now().isoformat()
                    }

                    df_nova = pd.DataFrame([row])
                    
                    for col in df_nova.columns:
                        if col not in df.columns:
                            df[col] = pd.Series(dtype='str')
                            
                    df = pd.concat([df, df_nova], ignore_index=True)
                    
                    save_users(df) 
                    st.success(f"{tipo} criado com sucesso!")
                    st.info(f"ID (Usuário): {row['username']} | Senha inicial: {senha}")


    # ==================== TURMAS (SEÇÃO ATUALIZADA) ====================
    if tab == "Turmas":
        st.markdown("---")
        st.subheader("Visão Geral de Turmas e Cursos")

        # --- 1. Carregar todos os dados ---
        df_usuarios = load_users()
        turmas = load_turmas()
        matriculas = load_matriculas()
        df_disciplinas = load_disciplinas() 

        # --- CORREÇÃO: Renomeia 'username' para 'id' e 'nome_completo' para 'nome' ---
        # Isto é crucial para os merges e lógicas seguintes
        if "id" not in df_usuarios.columns and "username" in df_usuarios.columns:
            df_usuarios = df_usuarios.rename(columns={"username": "id"})
        if "nome" not in df_usuarios.columns and "nome_completo" in df_usuarios.columns:
            df_usuarios = df_usuarios.rename(columns={"nome_completo": "nome"})
        # --- FIM DA CORREÇÃO ---

        if df_usuarios.empty: st.warning("Nenhum usuário cadastrado.")
        if turmas.empty: st.warning("Nenhuma turma cadastrada.")
        if df_disciplinas.empty: st.warning("Nenhuma disciplina cadastrada.")

        # --- 2. Lógica das Métricas ---
        total_cursos = len(df_cursos)
        
        if "role" not in df_usuarios.columns: df_usuarios["role"] = "" 
        if "status" not in df_usuarios.columns: df_usuarios["status"] = "ativo" 
        
        professores_ativos = df_usuarios[(df_usuarios["role"] == "Professor") & (df_usuarios["status"] == "ativo")]
        total_professores = len(professores_ativos)
        professores_ativos_ids = professores_ativos["id"].tolist()
        
        # CSV: id_turma, id_professor
        if "id_professor" not in turmas.columns:
             st.warning("Arquivo 'turmas.csv' não tem 'id_professor'. Métrica de turmas vagas pode falhar.")
             turmas["id_professor"] = pd.Series(dtype='str')
             
        turmas_sem_professor = turmas[~turmas['id_professor'].isin(professores_ativos_ids)]
        total_faltando = len(turmas_sem_professor)

        total_alunos = len(df_usuarios[df_usuarios["role"] == "Aluno"])

        # --- 3. Exibir Métricas ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📚 Cursos", total_cursos)
        col2.metric("👨‍🏫 Professores Ativos", total_professores)
        col3.metric("⚠️ Turmas Sem Professor", total_faltando)
        col4.metric("👨‍🎓 Alunos", total_alunos)

        # --- 4. Tabela de Visão Geral das Turmas ---
        st.markdown("### Turmas Abertas")
        
        if turmas.empty:
            st.info("Nenhuma turma cadastrada para exibir.")
        else:
            # CSV: id_turma
            # CSV: id_aluno, id_turma
            
            # Garante que a coluna de join em matriculas exista
            if "id_turma" not in matriculas.columns:
                matriculas["id_turma"] = ""
                st.warning("Arquivo 'matriculas.csv' não tem 'id_turma'.")

            # Garante que a coluna de contagem em matriculas exista
            if "id_aluno" not in matriculas.columns:
                matriculas["id_aluno"] = ""
                st.warning("Arquivo 'matriculas.csv' não tem 'id_aluno'.")

            if not matriculas.empty:
                # CORREÇÃO: Usa 'id_aluno' e 'id_turma'
                contagem = matriculas.groupby("id_turma")["id_aluno"].nunique().reset_index()
                contagem.columns = ["id_turma", "Alunos"]
                contagem["id_turma"] = contagem["id_turma"].astype(str)
            else:
                contagem = pd.DataFrame(columns=["id_turma", "Alunos"])
            
            turmas["id_turma"] = turmas["id_turma"].astype(str)
            # CORREÇÃO: Junta usando 'id_turma'
            turmas_merged = turmas.merge(contagem, on="id_turma", how="left")
            turmas_merged["Alunos"] = turmas_merged["Alunos"].fillna(0).astype(int)

            if not df_disciplinas.empty:
                turmas_merged = turmas_merged.merge(
                    df_disciplinas[["id_disciplina", "nome_disciplina"]],
                    on="id_disciplina", how="left"
                )
            else:
                turmas_merged["nome_disciplina"] = "N/A"

            # --- CORREÇÃO DO MERGEERROR ---
            # 1. Seleciona APENAS as colunas 'id' e 'nome' dos professores
            df_professores = df_usuarios[df_usuarios['role'] == 'Professor'][['id', 'nome']]
            
            # 2. Faz o merge.
            turmas_merged = turmas_merged.merge(
                df_professores,
                left_on="id_professor",
                right_on="id",
                how="left"
            )
            # 3. Renomeia a coluna 'nome' (do professor) para 'Professor'
            turmas_merged['Professor'] = turmas_merged['nome'].fillna("—")
            # --- FIM DA CORREÇÃO ---

            rename_map = {
                "id_turma": "Turma", "nome_disciplina": "Disciplina", "Professor": "Professor",
                "semestre": "Semestre", "horario_sala": "Horário", "Alunos": "Alunos"
            }
            
            turmas_renomeado = turmas_merged.rename(columns=rename_map)
            colunas_visiveis = [c for c in rename_map.values() if c in turmas_renomeado.columns]
            df_sem_indice = turmas_renomeado[colunas_visiveis].copy()
            
            st.dataframe(
                df_sem_indice,
                use_container_width=True,
                hide_index=True
            )

        # --- 5. Detalhamento por Curso ---
        st.markdown("---")
        st.subheader("Detalhamento por Curso (Alocação de Professores)")

        curso_nome_selecionado = st.selectbox("Selecione um curso para ver detalhes:", ["--"] + lista_cursos_nomes, disabled=not cursos_validos)

        if curso_nome_selecionado and curso_nome_selecionado != "--":
            id_curso_selecionado = df_cursos.loc[df_cursos['nome_curso'] == curso_nome_selecionado, 'id_curso'].iloc[0]
            
            if df_disciplinas.empty:
                st.warning("Não é possível mostrar o detalhamento pois 'disciplinas.csv' não foi carregado.")
            else:
                # CSV: id_disciplina, ..., id_curso
                if "id_curso" not in df_disciplinas.columns:
                    st.error("Erro Crítico: O arquivo 'disciplinas.csv' não contém a coluna 'id_curso' necessária para o filtro.")
                else:
                    disciplinas_do_curso = df_disciplinas[df_disciplinas["id_curso"] == id_curso_selecionado].copy()
                    
                    if disciplinas_do_curso.empty:
                        st.warning(f"Não há disciplinas cadastradas para o curso '{curso_nome_selecionado}'.")
                    else:
                        turmas_do_curso = turmas[turmas["id_disciplina"].isin(disciplinas_do_curso["id_disciplina"])].copy()
                        
                        df_det = disciplinas_do_curso.merge(
                            turmas_do_curso[["id_disciplina", "id_professor"]],
                            on="id_disciplina",
                            how="left"
                        )

                        df_professores = df_usuarios[df_usuarios['role'] == 'Professor'][['id', 'nome']]
                        df_det = df_det.merge(
                            df_professores,
                            left_on="id_professor",
                            right_on="id",
                            how="left"
                        )
                        df_det['Professor'] = df_det['nome'].fillna("—")

                        df_det['Situação'] = df_det['id_professor'].apply(
                            lambda x: "OK" if pd.notna(x) and x in professores_ativos_ids else "Sem professor / Inativo"
                        )

                        df_mostrar = df_det.rename(columns={
                            "codigo_disciplina": "Código",
                            "nome_disciplina": "Disciplina"
                        })
                        
                        colunas_detalhamento = ["Código", "Disciplina", "Professor", "Situação"]
                        colunas_finais = [c for c in colunas_detalhamento if c in df_mostrar.columns]
                        
                        st.dataframe(
                            df_mostrar[colunas_finais],
                            use_container_width=True,
                            hide_index=True
                        )

                        total_ok = (df_mostrar["Situação"] == "OK").sum()
                        total_disc = len(df_mostrar)
                        st.markdown(f"👨‍🏫 *Professores ativos alocados:* {total_ok}/{total_disc} disciplinas")
        else:
            st.info("Selecione um curso para visualizar as disciplinas e professores.")


if __name__ == "__main__":
    admin_panel()