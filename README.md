📘 SIGA-U — Sistema Integrado de Gestão Acadêmica

O SIGA-U é um sistema acadêmico desenvolvido em Python + Streamlit, criado como projeto universitário (PIM) para gerenciar usuários, autenticação, turmas, matrículas e painéis personalizados para diferentes perfis (Aluno, Professor, Coordenação e Administração).

O objetivo do sistema é oferecer uma solução simples, local e funcional para gestão interna de instituições de ensino.

🚀 Principais Funcionalidades

🔐 Autenticação com controle de acesso por perfil

👨‍🎓 Painel do Aluno

Visualização de informações

Acesso ao mural

Carteirinha

Calendário de prazos

👨‍🏫 Painel do Professor

Gerenciamento de prazos

Mural de recados

Visualização de turmas

🧑‍💼 Painel da Coordenação

Avaliação e aprovação de solicitações

Gerenciamento de turmas e cursos

🛠️ Painel do Administrador

Acesso geral

Gerenciamento de usuários

Gerenciamento do sistema

📁 Banco de dados local em CSV

🧩 Menu dinâmico, alterado automaticamente pelo tipo de usuário

🔄 Sessão segura, com logout que limpa o session_state

🗂️ Arquitetura em múltiplas páginas (Streamlit pages)

🧠 O que eu desenvolvi nesse projeto

Este sistema foi desenvolvido inteiramente por mim, incluindo:

✔️ Estruturação da arquitetura do sistema
✔️ Tratamento de autenticação e redirecionamento
✔️ Criação dos painéis personalizados (Aluno, Professor, Coordenação, Admin)
✔️ Implementação do menu lateral dinâmico
✔️ CRUD básico usando arquivos CSV
✔️ Organização das páginas dentro do Streamlit
✔️ Documentação completa (README técnico dentro das pastas)
✔️ Diagramas e estrutura do PIM (caso de uso, sequência, etc.)
✔️ Testes, ajustes e otimização para rodar em rede local

🧱 Tecnologias Utilizadas

Python 3

Streamlit

Pandas

CSV como banco de dados local

Git / GitHub para versionamento

🗂️ Estrutura do Projeto
SIGA-U/
│
├── main.py
├── pages/
│   ├── painel_aluno.py
│   ├── painel_professor.py
│   ├── painel_coordenacao.py
│   ├── painel_admin.py
│
├── utils/
│   ├── autenticacao.py
│   ├── helpers.py
│
├── database/
│   ├── usuarios.csv
│   ├── turmas.csv
│   ├── prazos.csv
│
└── README.md


▶️ Como Executar

Clone este repositório:

git clone https://github.com/zTalesz/SIGA-U


Instale as dependências:

pip install streamlit pandas


Execute o sistema:

streamlit run main.py


O sistema abre no navegador automaticamente.


📄 Documentação Técnica Completa

A documentação do projeto (manual de uso, descrição técnica e orientações do PIM) está incluída dentro das pastas do repositório.
