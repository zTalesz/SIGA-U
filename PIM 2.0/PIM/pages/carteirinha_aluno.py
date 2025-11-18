# pages/carteirinha_aluno.py (VERSÃO CORRIGIDA COM HTML E BASE64)

import sys
import os
import streamlit as st
import pandas as pd
import base64  # <-- Importante para converter a imagem

# 1. Bloco de importação de path (sys.path)
pages_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(pages_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 2. Imports das suas bibliotecas
from auth_utils import show_custom_menu
from config import get_csv_path

# 3. COMANDO Nº 1: st.set_page_config()
st.set_page_config(
    page_title="Minha Carteirinha",
    layout="wide"
)

# 4. COMANDO Nº 2: show_custom_menu()
show_custom_menu()

# 5. O resto do seu código
st.title("💳 Minha Carteirinha Estudantil")

# --- Função para converter imagem em Base64 ---
def get_image_as_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

# --- CSS Customizado para o Cartão ---
# Este CSS agora vai formatar o HTML que vamos construir
st.markdown("""
<style>
    .card-container {
        background-color: #004a91; 
        color: white;
        padding: 2rem;
        border-radius: 15px;
        max-width: 500px;
        margin: auto;
        border: 2px solid #fddd00;
        font-family: 'Source Sans Pro', sans-serif; /* Fonte padrão do Streamlit */
    }
    
    /* Estilo para a imagem do logo */
    .card-container img.logo {
        max-width: 200px; 
        height: auto;
        display: block; 
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Estilo para a linha divisória */
    .card-container hr {
        border-top: 1px solid #fddd00;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .student-info {
        padding-left: 0rem; 
    }
    .student-info .label {
        font-size: 0.9rem;
        font-weight: bold;
        color: #fddd00;
        margin-top: 12px;
    }
    .student-info .value {
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)


# --- Lógica para Carregar Dados da Carteirinha ---
try:
    aluno_id = st.session_state.user_info['id_usuario']
    
    df_usuarios = pd.read_csv(get_csv_path('usuarios.csv'))
    df_cursos = pd.read_csv(get_csv_path('cursos.csv')) 
    
    aluno_data = df_usuarios[df_usuarios['id_usuario'] == int(aluno_id)]
    
    if aluno_data.empty:
        st.error("Não foi possível encontrar seus dados de usuário.")
    else:
        aluno = aluno_data.iloc[0]
        
        try:
            id_curso_aluno = aluno['id_curso']
            nome_do_curso = df_cursos[df_cursos['id_curso'] == id_curso_aluno]['nome_curso'].iloc[0]
        except Exception:
            nome_do_curso = "Curso não definido" 
        
        # --- PREPARA O LOGO ---
        LOGO_PATH = get_csv_path('logo.png')
        logo_base64 = get_image_as_base64(LOGO_PATH)
        
        if logo_base64:
            logo_html = f'<img src="{logo_base64}" class="logo" alt="Logo SIGA-U">'
        else:
            logo_html = "<p style='text-align:center; color: #fddd00;'>Logo não encontrado</p>"
        
        # --- Constrói o HTML inteiro da Carteirinha ---
        html_carteirinha = f"""
        <div class="card-container">
            {logo_html}
            
            <hr>
            
            <div class="student-info">
                <div class="label">Nome:</div>
                <div class="value">{aluno['nome_completo']}</div>
                
                <div class="label">Matrícula:</div>
                <div class="value">{aluno['id_usuario']}</div>
                
                <div class="label">RG:</div>
                <div class="value">{aluno['rg']}</div>
                
                <div class="label">CPF:</div>
                <div class="value">{aluno['cpf']}</div>
                
                <div class="label">Campus:</div>
                <div class="value">{aluno['campus']}</div>
                
                <div class="label">Curso:</div>
                <div class="value">{nome_do_curso}</div>
                
                <div class="label">Validade:</div>
                <div class="value">{aluno['validade']}</div>
            </div>
        </div>
        """
        
        # --- Renderiza o HTML de uma só vez ---
        st.html(html_carteirinha)

except FileNotFoundError as e:
    st.error(f"ERRO: O arquivo '{e.filename}' não foi encontrado.")
    st.info("Verifique se o script 'gerar_dados_COMPLETOS.py' já foi executado.")
except KeyError as e:
    st.error(f"ERRO: A coluna {e} não foi encontrada no 'usuarios.csv'.")
    st.info("Verifique se o seu 'usuarios.csv' tem as colunas (rg, cpf, id_curso, campus, validade).")
except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {e}")