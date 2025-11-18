# 📘 SIGA-U — Sistema Integrado de Gestão Acadêmica

Sistema acadêmico desenvolvido em **Python + Streamlit**, com autenticação baseada em perfis, navegação personalizada e banco de dados local utilizando arquivos CSV.

O SIGA-U foi criado como projeto universitário (PIM), com objetivo de oferecer uma solução simples e funcional para gestão interna de instituições de ensino — totalmente local, sem necessidade de servidor ou internet.

---

# 🚀 Funcionalidades Principais

## 🔐 Autenticação e Controle de Acesso
- Login por **ID + senha** (ex: ADM25001, A25001, P25001)  
- Controle de sessão com `st.session_state`  
- Redirecionamento automático para o painel do perfil correto  
- Menus dinâmicos conforme o tipo de usuário

---

# 👤 Perfis de Usuário

## 🛠️ Administrador
- Gerenciar **usuários**
  - Criar professores  
  - Criar alunos  
  - Criar coordenadores  
  - Criar administradores  
- Gerenciar **turmas**  
- Visualizar estatísticas gerais

---

## 🧑‍🏫 Professor
- Visualizar turmas
- Registrar **frequência**
- Registrar **notas**
- Acessar mural de recados (painel exclusivo)

---

## 🎓 Aluno
- Ver **calendário**  
- Acessar **mural de recados**  
- Visualizar **carteirinha digital**  
- Análise de notas e frequência por disciplina  
- Painel com métricas de desempenho  

---

## 🧑‍💼 Coordenação
- Gerenciar prazos
- Acessar painel de gestão de disciplinas
- Visão geral das turmas

---

# 📂 Estrutura do Projeto

PIM_STREAMLIT/
│
├── data/
│ ├── usuarios.csv
│ ├── turmas.csv
│ ├── matriculas.csv
│ ├── disciplinas.csv
│ ├── cursos.csv
│ ├── notas.csv
│ ├── frequencia.csv
│ └── recados.csv
│
├── pages/
│ ├── painel_administracao.py
│ ├── painel_professor.py
│ ├── painel_coordenacao.py
│ ├── painel_aluno.py
│ ├── calendario_aluno.py
│ ├── mural_recados_aluno.py
│ └── gestao_prazos_professor.py
│
├── scripts/
│ ├── auth_utils.py
│ ├── utils.py
│ └── config.py
│
├── main.py
└── README.md



# 🛠️ Executando o Sistema

### ✔️ 1. Instalar dependências

pip install streamlit pandas

✔️ 2. Rodar o sistema

streamlit run main.py

O navegador abrirá automaticamente.

🧩 Funcionamento do Login
Trecho principal do main.py:

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
    
O login valida usando as colunas:

username
password
role


### 🔑 Formato mínimo do `usuarios.csv`:

| id_usuario | nome         | id        | role          | data_nascimento | cpf  | email          | curso_ou_disciplina | password | status | must_change_password |
|------------|--------------|-----------|---------------|-----------------|------|----------------|----------------------|----------|--------|------------------------|
| 1          | Admin Geral  | ADM25001  | Administrador | 1980-01-01      | ...  | admin@siga.com | 1234                 | ativo    | False  |

### Observações

- Senhas não são criptografadas (decisão para ambiente local/offline).  
- Administradores podem cadastrar novos usuários pelo painel.

---

# 🗃️ Banco de Dados Local

O sistema usa arquivos CSV para armazenar:

- **usuários**
- **turmas**
- **disciplinas**
- **matrículas**
- **frequência**
- **notas**
- **recados**

Nenhum banco externo é necessário.


🏷️ Autor
Tales Lima
Desenvolvedor • Python • Streamlit • Análise e Desenvolvimento de Sistemas
