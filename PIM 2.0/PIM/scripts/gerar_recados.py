import pandas as pd
import os
import sys
from datetime import date

# --- Configuração de Path ---
# Esta parte é importante para que o script encontre o 'config.py'
# Encontra o diretório do script (ex: .../PIM_STREAMLIT/scripts)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Sobe um nível para a raiz do projeto (ex: .../PIM_STREAMLIT/)
project_root = os.path.dirname(script_dir)
# Adiciona a raiz ao sys.path para permitir a importação do 'config'
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    # Tenta importar a função de configuração do seu projeto
    from config import get_csv_path
except ImportError:
    print("ERRO: Não foi possível encontrar o arquivo 'config.py'.")
    print("Certifique-se que este script está em uma pasta 'scripts' na raiz do seu projeto (junto com 'main.py').")
    sys.exit(1)

# --- Constantes ---
# O nome do arquivo que vamos criar
RECADOS_CSV_PATH = get_csv_path('recados.csv')
# As colunas que queremos no nosso novo CSV
HEADERS = ['id_recado', 'titulo', 'mensagem', 'autor_nome', 'autor_id', 'data_publicacao', 'publico_alvo_turma_id']

def gerar_recados():
    """
    Gera um 'recados.csv' de exemplo com base nos usuários (prof/coord)
    e turmas existentes.
    """
    print("Iniciando geração do 'recados.csv' de exemplo...")
    try:
        # 1. Carregar os dados fonte que fazem sentido
        # Precisamos de Autores (Professores, Coordenadores, Admins)
        df_usuarios = pd.read_csv(get_csv_path('usuarios.csv'))
        # Precisamos de Turmas (Público-alvo)
        df_turmas = pd.read_csv(get_csv_path('turmas.csv'))

        # 2. Encontrar Autores válidos
        # Vamos pegar qualquer usuário que NÃO seja 'Aluno'
        autores_validos = df_usuarios[df_usuarios['role'].str.lower() != 'aluno']
        
        if autores_validos.empty:
            print("AVISO: Nenhum Professor, Coordenador ou Admin encontrado em 'usuarios.csv'.")
            print("Usando autores padrão de fallback.")
            # Se não houver autores, criamos um de exemplo
            autor_geral = {"id_usuario": 0, "nome_completo": "Coordenação Acadêmica"}
            autor_prof = {"id_usuario": 1, "nome_completo": "Professor Padrão"}
        else:
            # Pega o primeiro autor da lista (provavelmente um admin ou coordenador)
            autor_geral = autores_validos.iloc[0].to_dict()
            # Tenta pegar um professor, se não houver, usa o mesmo autor geral
            prof_df = autores_validos[autores_validos['role'].str.lower() == 'professor']
            autor_prof = prof_df.iloc[0].to_dict() if not prof_df.empty else autor_geral

        # 3. Encontrar Turmas válidas
        turmas_ids = df_turmas['id_turma'].tolist()
        if not turmas_ids:
            print("AVISO: Nenhuma turma encontrada em 'turmas.csv'.")
            print("Usando IDs de turma padrão de fallback (1 e 2).")
            turma_1_id = "1"
            turma_2_id = "2"
        else:
            # Pega o ID da primeira turma
            turma_1_id = str(turmas_ids[0])
            # Pega o ID da segunda turma (ou da primeira se só houver uma)
            turma_2_id = str(turmas_ids[1]) if len(turmas_ids) > 1 else turma_1_id

        # 4. Criar a lista de recados de exemplo
        recados_data = [
            {
                "id_recado": 1,
                "titulo": "Boas-vindas ao Semestre!",
                "mensagem": "Olá a todos! A coordenação deseja um excelente semestre de muito aprendizado e sucesso. Fiquem atentos a este mural!",
                "autor_nome": autor_geral['nome_completo'],
                "autor_id": str(autor_geral['id_usuario']),
                "data_publicacao": date(2025, 10, 1).isoformat(),
                "publico_alvo_turma_id": "Geral" # 'Geral' é uma string especial para todos
            },
            {
                "id_recado": 2,
                "titulo": "Lembrete: Atividade",
                "mensagem": "Pessoal, não se esqueçam da atividade listada no portal. O prazo está se aproximando!",
                "autor_nome": autor_prof['nome_completo'],
                "autor_id": str(autor_prof['id_usuario']),
                "data_publicacao": date(2025, 10, 5).isoformat(),
                "publico_alvo_turma_id": turma_1_id # Recado para a Turma 1
            },
            {
                "id_recado": 3,
                "titulo": "Aviso de Prova P1",
                "mensagem": "Atenção: A nossa prova P1 será na semana que vem. O conteúdo cobre os capítulos 1 a 3.",
                "autor_nome": autor_prof['nome_completo'],
                "autor_id": str(autor_prof['id_usuario']),
                "data_publicacao": date(2025, 10, 10).isoformat(),
                "publico_alvo_turma_id": turma_2_id # Recado para a Turma 2
            },
            {
                "id_recado": 4,
                "titulo": "Horário da Biblioteca",
                "mensagem": "Informamos que a biblioteca terá seu horário estendido durante a semana de provas.",
                "autor_nome": autor_geral['nome_completo'],
                "autor_id": str(autor_geral['id_usuario']),
                "data_publicacao": date(2025, 10, 12).isoformat(),
                "publico_alvo_turma_id": "Geral" # Recado geral
            }
        ]

        # 5. Criar o DataFrame e Salvar no CSV
        df_recados = pd.DataFrame(recados_data, columns=HEADERS)
        df_recados.to_csv(RECADOS_CSV_PATH, index=False)
        
        print(f"\nSUCESSO! O arquivo 'recados.csv' foi gerado em:")
        print(f"{RECADOS_CSV_PATH}")
        print(f"Foram criados {len(df_recados)} recados de exemplo.")

    except FileNotFoundError as e:
        print(f"ERRO: Arquivo fonte não encontrado: {e.filename}")
        print("Por favor, certifique-se que 'usuarios.csv' e 'turmas.csv' existem na sua pasta 'data'.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# --- Executa a função quando o script é chamado ---
if __name__ == "__main__":
    gerar_recados()