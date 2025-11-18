📘 SIGA-U — Sistema Integrado de Gestão Acadêmica

Desenvolvido em Python + Streamlit | Banco de dados local em CSV

O SIGA-U é um sistema acadêmico simples e funcional que gerencia alunos, professores, coordenadores e administradores, com acesso baseado em perfis e execução totalmente local, sem necessidade de internet ou servidor.

🚀 Funcionalidades Principais
🔐 Autenticação

Login por ID + senha (ex: ADM25001, A25001, P25001)

Controle de sessão usando st.session_state

Redirecionamento automático para o painel correto (Aluno, Professor, Coordenação ou Administração)

👤 Perfis de Usuário
Administrador

Gerenciar usuários

Criar novos:

🧑‍🏫 Professores
🎓 Alunos
🧑‍💼 Coordenadores
🛠️ Administradores

Gerenciar turmas

Visualizar estatísticas gerais do sistema
Professor
Visualizar suas turmas
Registrar frequência
Registrar notas

Aluno

Ver calendário
Ver mural de recados
Ver carteirinha digital
Coordenação
Ver e editar prazos
Acessar painel de gestão de disciplinas

📂 Estrutura do Projeto
PIM_STREAMLIT/
│
├── data/
│   ├── usuarios.csv
│   ├── turmas.csv
│   ├── matriculas.csv
│   ├── disciplinas.csv
│   ├── cursos.csv
│   ├── notas.csv
│   ├── frequencia.csv
│   └── recados.csv
│
├── pages/
│   ├── painel_administração.py
│   ├── painel_professor.py
│   ├── painel_cordenação.py
│   ├── painel_aluno.py
│   ├── calendario_aluno.py
│   ├── mural_recados_aluno.py
│   └── gestão_prazos_professor.py
│
├── scripts/
│   ├── auth_utils.py
│   ├── utils.py
│   └── config.py
│
├── main.py
└── README.md

🛠️ Executando o Sistema
✔️ 1. Instalar dependências

No terminal:
pip install streamlit pandas


✔️ 2. Rodar o sistema

Dentro da pasta do projeto:

streamlit run main.py

O navegador abrirá automaticamente.


🧩 Como o Login Funciona
A função principal no main.py:

def authenticate(username, password):
    df = pd.read_csv("data/usuarios.csv", dtype=str)
    df['password'] = df['password'].astype(str)

    user_data = df[
        (df['username'] == username) &
        (df['password'] == password)
    ]

    if not user_data.empty:
        return user_data.iloc[0]
    return None


O login procura o usuário pelas colunas:

username
password
role
Importante: todos os usuários precisam ter essas colunas devidamente preenchidas.

🔑 Formato do CSV de Usuários (usuarios.csv)

Arquivo mínimo válido:

id_usuario	nome	id	role	data_nascimento	cpf	email	curso_ou_disciplina	password	status	must_change_password
1	Admin Geral	ADM25001	Administrador	1980-01-01	000...	admin@siga.com
		1234	ativo	False

Obs:

Administradores podem cadastrar professores e alunos direto pelo painel.
password não é criptografada no modo local (decisão para simplificar operações offline).


📊 Banco de Dados Local (CSV)

O sistema usa apenas arquivos CSV organizados em:

usuarios.csv
turmas.csv
disciplinas.csv
matriculas.csv
frequencia.csv
notas.csv
recados.csv
Nenhum banco externo é necessário.

🧱 Tecnologias usadas

Python 3.10+

Streamlit

Pandas

CSV Local Storage


🤝 Contribuição

Pull Requests e melhorias são bem-vindas.


🏷️ Autor

Tales Lima