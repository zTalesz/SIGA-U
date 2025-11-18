# scripts/gerar_dados_massa.py
import pandas as pd
import os
import random
import numpy as np
from faker import Faker
from tqdm import tqdm

## --- CONFIGURAÇÃO --- ##
NUM_ALUNOS = 5000
NUM_PROFESSORES = 300
NUM_COORDENADORES = 20
NUM_ADMINS = 5
NUM_DISCIPLINAS = 40
NUM_TURMAS = 300
MIN_TURMAS_POR_ALUNO = 6
MAX_TURMAS_POR_ALUNO = 10

# Inicializa o Faker para gerar dados em Português do Brasil
fake = Faker('pt_BR')

def gerar_dados_massa():
    print("Iniciando a geração de dados em massa. Isso pode levar um momento...")

    # --- ALTERAÇÃO AQUI: TORNANDO O CAMINHO INTELIGENTE ---
    # Pega o caminho do diretório do script atual (scripts)
    script_dir = os.path.dirname(__file__)
    # Sobe um nível para o diretório raiz do projeto (PIM_STREAMLIT)
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    # Define o caminho para a pasta de dados
    data_path = os.path.join(project_root, 'data')
    # --------------------------------------------------------
    
    # Cria o diretório 'data' se não existir
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # --- 1. USUÁRIOS ---
    print("Gerando usuários...")
    # (O resto do código para gerar os dados continua o mesmo)
    usuarios = []
    id_usuario_counter = 1
    
    # Gerar Admins
    for _ in range(NUM_ADMINS):
        nome = fake.name()
        username = f"admin{id_usuario_counter}"
        usuarios.append({'id_usuario': id_usuario_counter, 'nome_completo': nome, 'username': username, 'password': 'admin', 'role': 'Administração'})
        id_usuario_counter += 1
        
    # Gerar Coordenadores
    for _ in range(NUM_COORDENADORES):
        nome = fake.name()
        username = f"coord{id_usuario_counter}"
        usuarios.append({'id_usuario': id_usuario_counter, 'nome_completo': nome, 'username': username, 'password': 'coord', 'role': 'Coordenação'})
        id_usuario_counter += 1

    # Gerar Professores
    ids_professores = []
    for _ in range(NUM_PROFESSORES):
        nome = fake.name()
        username = f"{nome.split()[0].lower()}.{nome.split()[-1].lower()}"
        usuarios.append({'id_usuario': id_usuario_counter, 'nome_completo': nome, 'username': username, 'password': '123', 'role': 'Professor'})
        ids_professores.append(id_usuario_counter)
        id_usuario_counter += 1

    # Gerar Alunos
    ids_alunos = []
    for _ in tqdm(range(NUM_ALUNOS), desc="Gerando Alunos"):
        nome = fake.name()
        username = f"{nome.split()[0].lower()}.{nome.split()[-1].lower()}{random.randint(1,99)}"
        usuarios.append({'id_usuario': id_usuario_counter, 'nome_completo': nome, 'username': username, 'password': 'aluno', 'role': 'Aluno'})
        ids_alunos.append(id_usuario_counter)
        id_usuario_counter += 1
        
    df_usuarios = pd.DataFrame(usuarios)
    # --- ALTERAÇÃO AQUI: USA O CAMINHO COMPLETO ---
    df_usuarios.to_csv(os.path.join(data_path, 'usuarios.csv'), index=False)
    print(f"-> {len(df_usuarios)} usuários gerados.")

    # --- 2. DISCIPLINAS ---
    print("Gerando disciplinas...")
    disciplinas = []
    nomes_disciplinas = ['Cálculo', 'Física', 'Química', 'Algoritmos', 'Estrutura de Dados', 'Banco de Dados', 'Engenharia de Software', 'Redes de Computadores', 'Inteligência Artificial', 'Marketing Digital']
    for i in range(1, NUM_DISCIPLINAS + 1):
        nome = f"{random.choice(nomes_disciplinas)} {random.choice(['I', 'II', 'Avançada', 'Aplicada'])}"
        disciplinas.append({'id_disciplina': i, 'nome_disciplina': nome, 'codigo_disciplina': f"{nome[:3].upper()}{i}", 'carga_horaria': random.choice([40, 60, 80])})
    
    df_disciplinas = pd.DataFrame(disciplinas)
    ids_disciplinas = df_disciplinas['id_disciplina'].tolist()
    # --- ALTERAÇÃO AQUI: USA O CAMINHO COMPLETO ---
    df_disciplinas.to_csv(os.path.join(data_path, 'disciplinas.csv'), index=False)
    print(f"-> {len(df_disciplinas)} disciplinas geradas.")

    # --- 3. TURMAS ---
    print("Gerando turmas...")
    turmas = []
    for i in range(1, NUM_TURMAS + 1):
        turmas.append({
            'id_turma': i,
            'id_disciplina': random.choice(ids_disciplinas),
            'id_professor': random.choice(ids_professores),
            'semestre': '2025.2',
            'horario_sala': f"{fake.day_of_week()} {random.randint(19,21)}h-{random.randint(21,23)}h, Sala {random.choice(['A','B','C'])}{random.randint(100,300)}"
        })
    df_turmas = pd.DataFrame(turmas)
    ids_turmas = df_turmas['id_turma'].tolist()
    # --- ALTERAÇÃO AQUI: USA O CAMINHO COMPLETO ---
    df_turmas.to_csv(os.path.join(data_path, 'turmas.csv'), index=False)
    print(f"-> {len(df_turmas)} turmas geradas.")

    # --- 4. MATRÍCULAS ---
    print("Gerando matrículas...")
    matriculas = []
    id_matricula_counter = 1
    for aluno_id in tqdm(ids_alunos, desc="Gerando Matrículas"):
        num_turmas = random.randint(MIN_TURMAS_POR_ALUNO, MAX_TURMAS_POR_ALUNO)
        turmas_aluno = random.sample(ids_turmas, num_turmas)
        for turma_id in turmas_aluno:
            matriculas.append({'id_matricula': id_matricula_counter, 'id_aluno': aluno_id, 'id_turma': turma_id})
            id_matricula_counter += 1
    
    df_matriculas = pd.DataFrame(matriculas)
    # --- ALTERAÇÃO AQUI: USA O CAMINHO COMPLETO ---
    df_matriculas.to_csv(os.path.join(data_path, 'matriculas.csv'), index=False)
    print(f"-> {len(df_matriculas)} matrículas geradas.")

    # --- 5. NOTAS e FREQUÊNCIA ---
    print("Gerando notas e frequência...")
    notas = []
    frequencias = []
    id_nota_counter = 1
    id_frequencia_counter = 1
    datas_aulas = pd.to_datetime(pd.date_range(start="2025-08-01", end="2025-11-30")).strftime('%Y-%m-%d').tolist()

    for _, row in tqdm(df_matriculas.iterrows(), total=df_matriculas.shape[0], desc="Gerando Notas/Frequência"):
        for avaliacao in ['P1', 'P2']:
            notas.append({
                'id_nota': id_nota_counter,
                'id_matricula': row['id_matricula'],
                'tipo_avaliacao': avaliacao,
                'valor_nota': round(np.random.uniform(3.0, 10.0), 1)
            })
            id_nota_counter += 1
        for data_aula in random.sample(datas_aulas, 8):
            frequencias.append({
                'id_frequencia': id_frequencia_counter,
                'id_matricula': row['id_matricula'],
                'data_aula': data_aula,
                'status_presenca': random.choices(['Presente', 'Ausente'], weights=[0.9, 0.1], k=1)[0]
            })
            id_frequencia_counter += 1
            
    df_notas = pd.DataFrame(notas)
    # --- ALTERAÇÃO AQUI: USA O CAMINHO COMPLETO ---
    df_notas.to_csv(os.path.join(data_path, 'notas.csv'), index=False)
    print(f"-> {len(df_notas)} registros de notas gerados.")
    
    df_frequencia = pd.DataFrame(frequencias)
    # --- ALTERAÇÃO AQUI: USA O CAMINHO COMPLETO ---
    df_frequencia.to_csv(os.path.join(data_path, 'frequencia.csv'), index=False)
    print(f"-> {len(df_frequencia)} registros de frequência gerados.")
    
    print("/nTODOS OS DADOS FORAM GERADOS COM SUCESSO NO LOCAL CORRETO!")

if __name__ == '__main__':
    gerar_dados_massa()