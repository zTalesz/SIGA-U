# scripts/gerar_atividades.py

import pandas as pd
import os
import random
from datetime import date, timedelta

print("Iniciando gerador de base de atividades (garantindo 1 por aluno)...")

# --- 1. Configuração de Caminhos ---
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

    USUARIOS_CSV_PATH = os.path.join(DATA_DIR, 'usuarios.csv')
    MATRICULAS_CSV_PATH = os.path.join(DATA_DIR, 'matriculas.csv')
    TURMAS_CSV_PATH = os.path.join(DATA_DIR, 'turmas.csv') # Usado para obter lista completa de turmas
    ATIVIDADES_CSV_PATH = os.path.join(DATA_DIR, 'atividades.csv')

    print(f"Pasta de dados definida como: {DATA_DIR}")

except NameError:
    print("Aviso: __file__ não definido. Usando caminhos relativos.")
    DATA_DIR = 'data'
    USUARIOS_CSV_PATH = 'data/usuarios.csv'
    MATRICULAS_CSV_PATH = 'data/matriculas.csv'
    TURMAS_CSV_PATH = 'data/turmas.csv'
    ATIVIDADES_CSV_PATH = 'data/atividades.csv'

# --- 2. Definições ---
HEADERS_ATIVIDADES = ['id_atividade', 'id_turma', 'titulo', 'descricao', 'data_entrega']
NUMERO_EXTRA_ATIVIDADES_ALEATORIAS = 15 # Ajuste conforme necessário
HOJE = date.today()

TITULOS_EXEMPLO = [
    "Prova 1", "Trabalho em Grupo", "Exercício de Fixação", "Projeto Final",
    "Resenha Crítica", "Seminário", "Entrega de Código", "Lista de Exercícios"
]
DESCRICOES_EXEMPLO = [
    "Capítulos 1 a 5 do livro-texto.",
    "Apresentação em slides (mínimo 15).",
    "Resolver os exercícios pares da lista.",
    "Implementação da API conforme especificado.",
    "Análise do artigo 'O Futuro da IA'.",
    "Sem descrição detalhada."
]

# --- 3. Leitura de Dependências (Usuários, Matrículas, Turmas) ---
try:
    df_usuarios = pd.read_csv(USUARIOS_CSV_PATH)
    df_matriculas = pd.read_csv(MATRICULAS_CSV_PATH)
    df_turmas = pd.read_csv(TURMAS_CSV_PATH) # Ler para ter a lista completa de turmas

    if 'id_usuario' not in df_usuarios.columns or 'role' not in df_usuarios.columns:
        print(f"ERRO: O arquivo '{USUARIOS_CSV_PATH}' não contém 'id_usuario' ou 'role'.")
        exit()
    if 'id_aluno' not in df_matriculas.columns or 'id_turma' not in df_matriculas.columns:
        print(f"ERRO: O arquivo '{MATRICULAS_CSV_PATH}' não contém 'id_aluno' ou 'id_turma'.")
        exit()
    if 'id_turma' not in df_turmas.columns:
         print(f"ERRO: O arquivo '{TURMAS_CSV_PATH}' não contém a coluna 'id_turma'.")
         exit()

    # Filtrar apenas os alunos
    df_alunos = df_usuarios[df_usuarios['role'].str.lower() == 'aluno'].copy()
    if df_alunos.empty:
        print("ERRO: Nenhum usuário com role 'Aluno' encontrado no arquivo de usuários.")
        exit()

    todos_alunos_ids = df_alunos['id_usuario'].unique().tolist()
    print(f"Sucesso: {len(todos_alunos_ids)} IDs de alunos encontrados.")

    # Pegar todos os IDs de turmas válidas existentes
    ids_de_turmas_validas_geral = df_turmas['id_turma'].unique().tolist()
    if not ids_de_turmas_validas_geral:
        print(f"ERRO: Nenhuma turma encontrada em '{TURMAS_CSV_PATH}'.")
        exit()

except FileNotFoundError as e:
    print(f"ERRO: Arquivo de dependência não encontrado: {e.filename}")
    print("Por favor, execute o script 'criar_bases.py' primeiro ou certifique-se que os arquivos existem.")
    exit()
# CORREÇÃO AQUI: 'catch' foi trocado por 'except'
except Exception as e:
    print(f"ERRO inesperado ao ler arquivos CSV: {e}")
    exit()

# --- 4. Mapeamento Aluno -> Turmas ---
aluno_turmas_map = {}
alunos_sem_turma = []
print("Mapeando alunos para suas turmas...")

for aluno_id in todos_alunos_ids:
    turmas_do_aluno = df_matriculas[df_matriculas['id_aluno'] == aluno_id]['id_turma'].unique().tolist()
    if turmas_do_aluno:
        # Garante que a turma ainda existe no arquivo turmas.csv (opcional, boa prática)
        turmas_validas_do_aluno = [t_id for t_id in turmas_do_aluno if t_id in ids_de_turmas_validas_geral]
        if turmas_validas_do_aluno:
             aluno_turmas_map[aluno_id] = turmas_validas_do_aluno
        else:
             print(f"AVISO: Aluno ID {aluno_id} está matriculado em turmas ({turmas_do_aluno}) que não existem mais em '{TURMAS_CSV_PATH}'.")
             alunos_sem_turma.append(aluno_id)
    else:
        alunos_sem_turma.append(aluno_id)

if alunos_sem_turma:
    print("-" * 30)
    print(f"AVISO: Os seguintes IDs de alunos não foram encontrados em '{MATRICULAS_CSV_PATH}' ou suas turmas não são válidas:")
    print(alunos_sem_turma)
    print("Estes alunos não terão atividades garantidas.")
    print("-" * 30)

# --- 5. Geração das Atividades (Garantidas + Aleatórias) ---
atividades_data = []
current_atividade_id = 0

# 5.1 Gerar uma atividade garantida para cada aluno matriculado
print(f"Gerando 1 atividade garantida para cada um dos {len(aluno_turmas_map)} alunos matriculados...")
for aluno_id, turmas_possiveis in aluno_turmas_map.items():
    current_atividade_id += 1
    id_turma_escolhida = random.choice(turmas_possiveis) # Escolhe uma das turmas do aluno

    dias_offset = random.randint(1, 45) # Gera datas futuras para atividades garantidas
    data_entrega = HOJE + timedelta(days=dias_offset)

    atividade = {
        'id_atividade': current_atividade_id,
        'id_turma': id_turma_escolhida,
        'titulo': f"{random.choice(TITULOS_EXEMPLO)} (Aluno {aluno_id})",
        'descricao': random.choice(DESCRICOES_EXEMPLO),
        'data_entrega': data_entrega.isoformat() # Formato AAAA-MM-DD
    }
    atividades_data.append(atividade)

print(f"{len(atividades_data)} atividades garantidas geradas.")

# 5.2 Gerar atividades aleatórias extras
print(f"Gerando {NUMERO_EXTRA_ATIVIDADES_ALEATORIAS} atividades aleatórias extras...")
for i in range(NUMERO_EXTRA_ATIVIDADES_ALEATORIAS):
    current_atividade_id += 1
    id_turma_aleatoria = random.choice(ids_de_turmas_validas_geral) # Escolhe de TODAS as turmas

    dias_offset = random.randint(-15, 45) # Pode ser passada ou futura
    data_entrega = HOJE + timedelta(days=dias_offset)

    atividade = {
        'id_atividade': current_atividade_id,
        'id_turma': id_turma_aleatoria,
        'titulo': f"{random.choice(TITULOS_EXEMPLO)} (Extra {i+1})",
        'descricao': random.choice(DESCRICOES_EXEMPLO),
        'data_entrega': data_entrega.isoformat() # Formato AAAA-MM-DD
    }
    atividades_data.append(atividade)

# --- 6. Criação do DataFrame e Salvamento do CSV ---
try:
    df_atividades = pd.DataFrame(atividades_data, columns=HEADERS_ATIVIDADES)
    # Ordenar por data de entrega pode ser mais útil para visualização inicial
    df_atividades = df_atividades.sort_values(by='data_entrega', ascending=True)

    df_atividades.to_csv(ATIVIDADES_CSV_PATH, index=False)
    print("-" * 60)
    print(f"SUCESSO! Arquivo '{ATIVIDADES_CSV_PATH}' foi criado/sobrescrito.")
    print(f"Total de {len(df_atividades)} atividades geradas:")
    print(f"  - {len(aluno_turmas_map)} atividades garantidas (1 por aluno matriculado).")
    print(f"  - {NUMERO_EXTRA_ATIVIDADES_ALEATORIAS} atividades aleatórias extras.")
    print("-" * 60)

except Exception as e:
    print(f"ERRO: Falha ao salvar o arquivo '{ATIVIDADES_CSV_PATH}': {e}")