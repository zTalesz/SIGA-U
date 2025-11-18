import pandas as pd
from faker import Faker
import random
import os
from datetime import datetime, timedelta

# Inicializa o Faker para gerar dados em português do Brasil
fake = Faker('pt_BR')

# --- CONFIGURAÇÃO DA GERAÇÃO ---
NUM_ALUNOS = 5000
NUM_PROFESSORES = 356
NUM_COORDENADORES = 30
NUM_TURMAS = 200

# Caminho para a pasta de dados
DATA_DIR = 'data'

def generate_usuarios():
    """Gera a lista de todos os usuários do sistema."""
    usuarios = []
    user_id_counter = 1

    # 1. Administrador
    usuarios.append({
        'user_id': user_id_counter,
        'nome_completo': 'Admin Geral',
        'username': 'admin',
        'password': 'admin', # Senha simples para protótipo
        'role': 'Administração'
    })
    user_id_counter += 1

    # 2. Coordenadores
    for _ in range(NUM_COORDENADORES):
        nome = fake.name()
        username = f"{nome.split(' ')[0].lower()}.coord"
        usuarios.append({
            'user_id': user_id_counter, 'nome_completo': nome, 'username': username,
            'password': 'coord', 'role': 'Coordenação'
        })
        user_id_counter += 1
    
    # 3. Professores
    professores = []
    for _ in range(NUM_PROFESSORES):
        nome = fake.name()
        username = f"{nome.split(' ')[0].lower()}.prof"
        professor = {
            'user_id': user_id_counter, 'nome_completo': nome, 'username': username,
            'password': 'prof', 'role': 'Professor'
        }
        usuarios.append(professor)
        professores.append(professor)
        user_id_counter += 1

    # 4. Alunos
    alunos = []
    for _ in range(NUM_ALUNOS):
        nome = fake.name()
        username = f"{nome.split(' ')[0].lower()}.aluno"
        aluno = {
            'user_id': user_id_counter, 'nome_completo': nome, 'username': username,
            'password': 'aluno', 'role': 'Aluno'
        }
        usuarios.append(aluno)
        alunos.append(aluno)
        user_id_counter += 1

    return usuarios, alunos, professores

def generate_turmas(professores):
    """Gera as turmas, associando a um professor."""
    disciplinas = ["Engenharia de Software", "Banco de Dados", "Redes de Computadores", "Inteligência Artificial", "Cálculo I", "Algoritmos Avançados"]
    turmas = []
    for i in range(1, NUM_TURMAS + 1):
        turmas.append({
            'turma_id': 100 + i,
            'nome_turma': f"{random.choice(disciplinas)} - 2025.2",
            'professor_id': random.choice([p['user_id'] for p in professores])
        })
    return turmas

def generate_matriculas(alunos, turmas):
    """Matricula alunos em turmas aleatoriamente."""
    matriculas = []
    matricula_id_counter = 1
    for aluno in alunos:
        num_matriculas = random.randint(1, 3) # Cada aluno em 1 a 3 turmas
        turmas_escolhidas = random.sample(turmas, num_matriculas)
        for turma in turmas_escolhidas:
            matriculas.append({
                'matricula_id': matricula_id_counter,
                'aluno_id': aluno['user_id'],
                'turma_id': turma['turma_id']
            })
            matricula_id_counter += 1
    return matriculas

def generate_dados_academicos(matriculas, turmas):
    """Gera notas, frequência, atividades e entregas."""
    notas, frequencia, atividades, entregas = [], [], [], []
    nota_id, freq_id, ativ_id, entrega_id = 1, 1, 1, 1

    # Gera atividades para cada turma
    for turma in turmas:
        for i in range(random.randint(1, 3)): # 1 a 3 atividades por turma
            atividades.append({
                'atividade_id': ativ_id,
                'turma_id': turma['turma_id'],
                'titulo': f'Trabalho {i+1} - {fake.bs()}',
                'descricao': fake.paragraph(nb_sentences=3),
                'data_entrega': (datetime.now() + timedelta(days=random.randint(15, 60))).strftime('%Y-%m-%d')
            })
            ativ_id += 1
            
    # Gera dados por matrícula
    for matricula in matriculas:
        # Gerar Notas
        for avaliacao in ["Prova 1", "Trabalho Final"]:
            notas.append({
                'nota_id': nota_id, 'matricula_id': matricula['matricula_id'],
                'avaliacao': avaliacao, 'nota': round(random.uniform(4.5, 10.0), 1)
            })
            nota_id += 1
        
        # Gerar Frequência
        for i in range(5): # 5 registros de aula
            data_aula = (datetime.now() - timedelta(days=7*i)).strftime('%Y-%m-%d')
            status = random.choices(['Presente', 'Falta'], weights=[0.9, 0.1], k=1)[0]
            frequencia.append({
                'frequencia_id': freq_id, 'matricula_id': matricula['matricula_id'],
                'data_aula': data_aula, 'status': status
            })
            freq_id += 1
            
        # Gerar Entregas
        atividades_da_turma = [a for a in atividades if a['turma_id'] == matricula['turma_id']]
        if atividades_da_turma and random.random() > 0.3: # 70% de chance de entregar
            atividade_escolhida = random.choice(atividades_da_turma)
            entregas.append({
                'entrega_id': entrega_id,
                'atividade_id': atividade_escolhida['atividade_id'],
                'aluno_id': matricula['aluno_id'],
                'path_arquivo': f"{fake.word()}_{matricula['aluno_id']}.pdf",
                'data_envio': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            entrega_id += 1

    return notas, frequencia, atividades, entregas

def main():
    """Função principal para gerar e salvar todos os arquivos CSV."""
    print("Iniciando a geração de dados para o SIGA-U...")

    # Garante que o diretório de dados exista
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Diretório '{DATA_DIR}' criado.")

    # Gerar dados
    usuarios, alunos, professores = generate_usuarios()
    turmas = generate_turmas(professores)
    matriculas = generate_matriculas(alunos, turmas)
    notas, frequencia, atividades, entregas = generate_dados_academicos(matriculas, turmas)

    # Criar DataFrames
    df_usuarios = pd.DataFrame(usuarios)
    df_turmas = pd.DataFrame(turmas)
    df_matriculas = pd.DataFrame(matriculas)
    df_notas = pd.DataFrame(notas)
    df_frequencia = pd.DataFrame(frequencia)
    df_atividades = pd.DataFrame(atividades)
    df_entregas = pd.DataFrame(entregas)
    
    # Salvar em CSV
    df_usuarios.to_csv(f'{DATA_DIR}/usuarios.csv', index=False)
    df_turmas.to_csv(f'{DATA_DIR}/turmas.csv', index=False)
    df_matriculas.to_csv(f'{DATA_DIR}/matriculas.csv', index=False)
    df_notas.to_csv(f'{DATA_DIR}/notas.csv', index=False)
    df_frequencia.to_csv(f'{DATA_DIR}/frequencia.csv', index=False)
    df_atividades.to_csv(f'{DATA_DIR}/atividades.csv', index=False)
    df_entregas.to_csv(f'{DATA_DIR}/entregas_atividades.csv', index=False)
    
    print("\nArquivos CSV gerados com sucesso na pasta 'data/':")
    print(f"- {len(df_usuarios)} usuários")
    print(f"- {len(df_turmas)} turmas")
    print(f"- {len(df_matriculas)} matrículas")
    print(f"- {len(df_notas)} registros de notas")
    print(f"- {len(df_frequencia)} registros de frequência")
    print(f"- {len(df_atividades)} atividades publicadas")
    print(f"- {len(df_entregas)} entregas de alunos")

if __name__ == '__main__':
    main()