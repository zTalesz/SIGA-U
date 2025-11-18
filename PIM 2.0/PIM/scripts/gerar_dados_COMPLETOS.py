import pandas as pd
import os
import sys
import random
from faker import Faker
from datetime import date, timedelta
import time # Para medir o tempo de execução

# --- Configuração de Path ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from config import get_csv_path
except ImportError:
    print("ERRO: Não foi possível encontrar o 'config.py'.")
    sys.exit(1)

# --- Configurações Iniciais ---
fake = Faker('pt_BR')
DATA_PATH = get_csv_path('') 
os.makedirs(DATA_PATH, exist_ok=True) 

# --- Listas para guardar os dados gerados ---
cursos_data = []
disciplinas_data = []
usuarios_data = []
turmas_data = []
matriculas_data = []
notas_data = []
frequencia_data = []
atividades_data = []
recados_data = []

# IDs globais para garantir unicidade
id_disciplina_global = 1
id_usuario_global = 1
id_turma_global = 1
id_matricula_global = 1
id_nota_global = 1
id_frequencia_global = 1
id_atividade_global = 1
id_recado_global = 1

start_time = time.time()
print(f"Iniciando a geração em larga escala na pasta: {DATA_PATH}")

# ==========================================================
# 1. GERAR CURSOS E DISCIPLINAS (7 Cursos, 6 Disc/Curso)
# ==========================================================
def gerar_cursos_e_disciplinas():
    global id_disciplina_global
    
    cursos_para_gerar = [
        (1, "Análise e Des. de Sistemas", [
            ("Lógica de Programação", "ADS101", 80), ("Engenharia de Software", "ADS102", 40),
            ("Banco de Dados", "ADS103", 80), ("Redes de Computadores", "ADS104", 40),
            ("Segurança da Informação", "ADS105", 40), ("Sistemas Operacionais", "ADS106", 40)
        ]),
        (2, "Engenharia Civil", [
            ("Cálculo I", "ECV101", 80), ("Física Geral", "ECV102", 80),
            ("Desenho Técnico", "ECV103", 40), ("Resistência dos Materiais", "ECV104", 80),
            ("Estruturas de Concreto", "ECV105", 40), ("Hidráulica", "ECV106", 40)
        ]),
        (3, "Direito", [
            ("Direito Constitucional", "DIR101", 80), ("Direito Penal I", "DIR102", 80),
            ("Direito Civil I", "DIR103", 80), ("Teoria Geral do Estado", "DIR104", 40),
            ("Economia Política", "DIR105", 40), ("Português Jurídico", "DIR106", 40)
        ]),
        (4, "Psicologia", [
            ("Psicologia Geral", "PSI101", 80), ("Neuroanatomia", "PSI102", 40),
            ("Filosofia", "PSI103", 40), ("Sociologia", "PSI104", 40),
            ("Teorias da Personalidade", "PSI105", 80), ("Metodologia Científica", "PSI106", 40)
        ]),
        (5, "Arquitetura e Urbanismo", [
            ("Desenho Arquitetônico", "ARQ101", 80), ("História da Arte", "ARQ102", 40),
            ("Geometria Descritiva", "ARQ103", 80), ("Plástica", "ARQ104", 40),
            ("Topografia", "ARQ105", 40), ("Conforto Ambiental", "ARQ106", 80)
        ]),
        (6, "Administração", [
            ("Teoria da Administração", "ADM101", 80), ("Contabilidade Básica", "ADM102", 80),
            ("Matemática Financeira", "ADM103", 80), ("Marketing", "ADM104", 40),
            ("Gestão de Pessoas", "ADM105", 40), ("Direito Empresarial", "ADM106", 40)
        ]),
        (7, "Medicina Veterinária", [
            ("Anatomia Animal", "VET101", 80), ("Bioquímica", "VET102", 80),
            ("Genética", "VET103", 40), ("Microbiologia", "VET104", 80),
            ("Histologia", "VET105", 40), ("Parasitologia", "VET106", 40)
        ])
    ]
    
    total_disciplinas = 0
    for id_curso, nome_curso, disciplinas_lista in cursos_para_gerar:
        cursos_data.append({
            "id_curso": id_curso,
            "nome_curso": nome_curso
        })
        
        for nome_disc, cod_disc, carga in disciplinas_lista:
            disciplinas_data.append({
                "id_disciplina": id_disciplina_global,
                "nome_disciplina": nome_disc,
                "codigo_disciplina": cod_disc,
                "carga_horaria": carga,
                "id_curso": id_curso 
            })
            id_disciplina_global += 1
            total_disciplinas += 1
            
    pd.DataFrame(cursos_data).to_csv(get_csv_path('cursos.csv'), index=False)
    pd.DataFrame(disciplinas_data).to_csv(get_csv_path('diciplinas.csv'), index=False)
    print(f"-> {len(cursos_data)} 'cursos.csv' e {total_disciplinas} 'diciplinas.csv' gerados.")

# ==========================================================
# 2. GERAR USUÁRIOS (2002 Alunos, 100 Prof, 50 Coord, 20 Adm)
# ==========================================================
def gerar_usuarios():
    global id_usuario_global
    
    # --- Configurações de Quantidade ---
    NUM_ALUNOS_POR_CURSO = 286 # (286 * 7 cursos = 2002 alunos)
    NUM_PROFESSORES = 100
    NUM_COORDENADORES = 50
    NUM_ADMINS = 20

    campus_list = ["Marquês", "Tatuapé", "Paulista", "Pinheiros", "Berrini"]
    
    # --- Gerar Alunos ---
    total_alunos = 0
    for curso in cursos_data:
        id_curso = curso['id_curso']
        for _ in range(NUM_ALUNOS_POR_CURSO):
            nome = fake.name()
            username = nome.split(' ')[0].lower() + str(id_usuario_global)
            usuarios_data.append({
                "id_usuario": id_usuario_global, "nome_completo": nome, "username": username,
                "password": "123", "role": "Aluno", "rg": fake.rg(), "cpf": fake.cpf(),
                "id_curso": id_curso, "campus": random.choice(campus_list),
                "validade": f"12/{random.randint(2026, 2029)}",
                "path_foto": f"fotos/{id_usuario_global}.jpg"
            })
            id_usuario_global += 1
            total_alunos += 1
    print(f"-> {total_alunos} Alunos gerados.")

    # --- Gerar 99 Professores Aleatórios ---
    for _ in range(NUM_PROFESSORES - 1):
        nome = fake.name()
        username = nome.split(' ')[0].lower() + str(id_usuario_global)
        usuarios_data.append({
            "id_usuario": id_usuario_global, "nome_completo": nome, "username": username,
            "password": "456", "role": "Professor", "rg": fake.rg(), "cpf": fake.cpf(),
            "id_curso": None, "campus": None, "validade": None, "path_foto": None
        })
        id_usuario_global += 1
    
    # --- GERAR O PROFESSOR "BRENDO VIEIRA" PARA TESTE ---
    usuarios_data.append({
        "id_usuario": id_usuario_global, "nome_completo": "Brendo Vieira", "username": "brendo",
        "password": "456", "role": "Professor", "rg": fake.rg(), "cpf": fake.cpf(),
        "id_curso": None, "campus": None, "validade": None, "path_foto": None
    })
    id_usuario_global += 1
    print(f"-> {NUM_PROFESSORES} Professores gerados (incluindo 'Brendo Vieira').")

    # --- Gerar Coordenadores ---
    for _ in range(NUM_COORDENADORES - 1):
        nome = fake.name()
        username = nome.split(' ')[0].lower() + str(id_usuario_global)
        usuarios_data.append({
            "id_usuario": id_usuario_global, "nome_completo": nome, "username": username,
            "password": "789", "role": "Coordenação", "rg": fake.rg(), "cpf": fake.cpf(),
            "id_curso": None, "campus": None, "validade": None, "path_foto": None
        })
        id_usuario_global += 1
    usuarios_data.append({
        "id_usuario": id_usuario_global, "nome_completo": "Rebeca da Cunha", "username": "rebeca",
        "password": "789", "role": "Coordenação", "rg": fake.rg(), "cpf": fake.cpf(),
        "id_curso": None, "campus": None, "validade": None, "path_foto": None
    })
    id_usuario_global += 1
    print(f"-> {NUM_COORDENADORES} Coordenadores gerados (incluindo 'rebeca').")
    
    # --- Gerar Administradores ---
    for _ in range(NUM_ADMINS - 1):
        nome = fake.name()
        username = nome.split(' ')[0].lower() + str(id_usuario_global)
        usuarios_data.append({
            "id_usuario": id_usuario_global, "nome_completo": nome, "username": username,
            "password": "999", "role": "Administração", "rg": fake.rg(), "cpf": fake.cpf(),
            "id_curso": None, "campus": None, "validade": None, "path_foto": None
        })
        id_usuario_global += 1
    usuarios_data.append({
        "id_usuario": id_usuario_global, "nome_completo": "Administrador Mestre", "username": "admin",
        "password": "999", "role": "Administração", "rg": fake.rg(), "cpf": fake.cpf(),
        "id_curso": None, "campus": None, "validade": None, "path_foto": None
    })
    id_usuario_global += 1
    print(f"-> {NUM_ADMINS} Administradores gerados (incluindo 'admin').")
            
    pd.DataFrame(usuarios_data, columns=[
        "id_usuario", "nome_completo", "username", "password", "role", 
        "rg", "cpf", "id_curso", "campus", "validade", "path_foto"
    ]).to_csv(get_csv_path('usuarios.csv'), index=False)
    print(f"-> 'usuarios.csv' salvo com {len(usuarios_data)} usuários.")

# ==========================================================
# 3. GERAR TURMAS E MATRÍCULAS (CORRIGIDO PARA GARANTIR 1 TURMA POR PROF)
# ==========================================================
def gerar_turmas_e_matriculas():
    global id_turma_global, id_matricula_global
    
    professores_ids = [u['id_usuario'] for u in usuarios_data if u['role'] == 'Professor']
    if not professores_ids:
        raise ValueError("Nenhum professor foi gerado. Impossível criar turmas.")
        
    # --- NOVA LÓGICA DE GERAÇÃO DE TURMAS ---
    # Garante que cada professor tenha pelo menos uma turma.
    
    num_professores = len(professores_ids) # 100
    
    # Temos 42 disciplinas
    disciplinas_lista = disciplinas_data 
    num_disciplinas = len(disciplinas_lista) # 42
    
    if num_disciplinas == 0:
         raise ValueError("Nenhuma disciplina foi gerada. Impossível criar turmas.")
    
    # Embaralha os professores para que a atribuição de disciplina seja aleatória
    random.shuffle(professores_ids)
    
    print(f"-> Alocando {num_professores} professores em {num_disciplinas} disciplinas...")

    # Loop 100 vezes (uma por professor)
    for i in range(num_professores):
        professor_id = professores_ids[i] # Pega o professor da vez
        
        # Atribui uma disciplina de forma cíclica (usando módulo)
        disciplina_para_esta_turma = disciplinas_lista[i % num_disciplinas]
        
        turmas_data.append({
            "id_turma": id_turma_global,
            "id_disciplina": disciplina_para_esta_turma['id_disciplina'],
            "id_professor": professor_id, # CADA professor recebe exatamente uma turma
            "semestre": f"2025.{random.randint(1, 2)}",
            "horario_sala": f"{random.choice(['Seg', 'Ter', 'Qua'])} 19h-21h / Sala B{random.randint(100, 110)}"
        })
        id_turma_global += 1
    
    print(f"-> {len(turmas_data)} 'turmas.csv' geradas (uma para cada professor).")
    # --- FIM DA NOVA LÓGICA ---
        
    # Matricular alunos
    df_disciplinas = pd.DataFrame(disciplinas_data)
    df_turmas = pd.DataFrame(turmas_data)
    
    num_matriculas = 0
    for aluno in [u for u in usuarios_data if u['role'] == 'Aluno']:
        aluno_id = aluno['id_usuario']
        curso_id = aluno['id_curso']
        
        disciplinas_do_curso_ids = df_disciplinas[df_disciplinas['id_curso'] == curso_id]['id_disciplina'].tolist()
        turmas_do_curso_ids = df_turmas[df_turmas['id_disciplina'].isin(disciplinas_do_curso_ids)]['id_turma'].tolist()
        
        num_a_matricular = min(len(turmas_do_curso_ids), 5) 
        if num_a_matricular > 0:
            turmas_para_matricular = random.sample(turmas_do_curso_ids, num_a_matricular)
            
            for turma_id in turmas_para_matricular:
                matriculas_data.append({
                    "id_matricula": id_matricula_global,
                    "id_aluno": aluno_id,
                    "id_turma": turma_id
                })
                id_matricula_global += 1
                num_matriculas += 1

    pd.DataFrame(matriculas_data).to_csv(get_csv_path('matriculas.csv'), index=False)
    print(f"-> {num_matriculas} 'matriculas.csv' geradas.")

# ==========================================================
# 4. GERAR DEPENDENTES (Notas, Frequência, Atividades, Recados)
# ==========================================================
def gerar_dependentes():
    global id_nota_global, id_frequencia_global, id_atividade_global, id_recado_global
    
    print("Iniciando geração de dependentes (isso pode levar alguns segundos)...")
    hoje = date.today()
    
    # Para cada matrícula, gerar notas e frequência
    num_notas = 0
    num_frequencias = 0
    
    # Otimização: para não sobrecarregar, gerar para no máximo 10000 matrículas
    matriculas_sample = matriculas_data
    if len(matriculas_data) > 10000:
        matriculas_sample = random.sample(matriculas_data, 10000)
        print(f"-> Otimização: Gerando notas/frequência para 10.000 matrículas (de {len(matriculas_data)})")

    for matricula in matriculas_sample:
        id_mat = matricula['id_matricula']
        
        # Gerar Notas (P1, P2)
        notas_data.append({"id_nota": id_nota_global, "id_matricula": id_mat, "tipo_avaliacao": "P1", "valor_nota": round(random.uniform(3.0, 9.5), 1)})
        id_nota_global += 1
        notas_data.append({"id_nota": id_nota_global, "id_matricula": id_mat, "tipo_avaliacao": "P2", "valor_nota": round(random.uniform(4.0, 10.0), 1)})
        id_nota_global += 1
        num_notas += 2
        
        # Gerar Frequência (ex: 5 aulas passadas)
        for i in range(5):
            data_aula = (hoje - timedelta(days=(i*7)))
            frequencia_data.append({
                "id_frequencia": id_frequencia_global,
                "id_matricula": id_mat,
                "data_aula": data_aula.isoformat(),
                "status_presenca": random.choice(["Presente", "Presente", "Presente", "Ausente"])
            })
            id_frequencia_global += 1
            num_frequencias += 1

    # Gerar Atividades (1 por turma)
    for turma in turmas_data:
        id_turma = turma['id_turma']
        atividades_data.append({
            "id_atividade": id_atividade_global,
            "id_turma": id_turma,
            "titulo": f"Trabalho 1 - {turma['semestre']}",
            "descricao": "Entregar o trabalho conforme especificações.",
            "data_entrega": (hoje + timedelta(days=random.randint(10, 30))).isoformat()
        })
        id_atividade_global += 1

    # Gerar Recados (5 de exemplo)
    autores_staff = [u for u in usuarios_data if u['role'] != 'Aluno']
    for i in range(5): 
        autor = random.choice(autores_staff)
        recados_data.append({
            "id_recado": id_recado_global,
            "titulo": f"Aviso Importante {i+1}",
            "mensagem": "Este é um comunicado de exemplo gerado pelo script.",
            "autor_nome": autor['nome_completo'],
            "autor_id": autor['id_usuario'],
            "data_publicacao": (hoje - timedelta(days=i)).isoformat(),
            "publico_alvo_turma_id": "Geral" 
        })
        id_recado_global += 1

    # Salvar CSVs
    pd.DataFrame(notas_data).to_csv(get_csv_path('notas.csv'), index=False)
    pd.DataFrame(frequencia_data).to_csv(get_csv_path('frequencia.csv'), index=False)
    pd.DataFrame(atividades_data).to_csv(get_csv_path('atividades.csv'), index=False)
    pd.DataFrame(recados_data, columns=
        ['id_recado', 'titulo', 'mensagem', 'autor_nome', 'autor_id', 'data_publicacao', 'publico_alvo_turma_id']
    ).to_csv(get_csv_path('recados.csv'), index=False)
    print(f"-> {num_notas} 'notas.csv', {num_frequencias} 'frequencia.csv' gerados.")
    print(f"-> {len(atividades_data)} 'atividades.csv' e {len(recados_data)} 'recados.csv' gerados.")

# ==========================================================
# EXECUTAR TUDO NA ORDEM CORRETA
# ==========================================================
def main():
    try:
        gerar_cursos_e_disciplinas()
        gerar_usuarios()
        gerar_turmas_e_matriculas()
        gerar_dependentes()
        
        end_time = time.time()
        print("\n--- SUCESSO! ---")
        print(f"Todos os 9 arquivos CSV foram gerados e estão interligados.")
        print(f"Total de {len(usuarios_data)} usuários e {len(matriculas_data)} matrículas.")
        print(f"Tempo total de execução: {end_time - start_time:.2f} segundos.")
        
    except Exception as e:
        print(f"\n--- ERRO ---")
        print(f"Ocorreu um erro durante a geração dos dados: {e}")
        print("Verifique se as bibliotecas (pandas, faker) estão instaladas.")

if __name__ == "__main__":
    main()