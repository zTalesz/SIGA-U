# main.py (ATUALIZADO)

import streamlit as st
import pandas as pd
from auth_utils import show_custom_menu
import time

st.set_page_config(page_title="SIGA-U Login", page_icon="🎓", layout="centered")

def authenticate(username, password):
    """Verifica as credenciais no CSV de usuários."""
    try:
        df_usuarios = pd.read_csv('data/usuarios.csv')
        # Garante que a senha do CSV seja tratada como string
        df_usuarios['password'] = df_usuarios['password'].astype(str)
        user_data = df_usuarios[(df_usuarios    ['username'] == username) & (df_usuarios['password'] == str(password))]
        
        if not user_data.empty:
            return user_data.iloc[0]
        return None
    except FileNotFoundError:
        return "FILE_NOT_FOUND"

# --- Inicialização do Session State ---
# 'logged_in' controla o status
# 'redirect_to_dashboard' é um novo flag que controla o redirecionamento PÓS-LOGIN
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = None
    st.session_state['redirect_to_dashboard'] = False

# --- LÓGICA PRINCIPAL ---

# 1. Se o usuário ESTÁ logado
if st.session_state['logged_in']:
    
    # 1.1 Se ele ACABOU de fazer login (flag de redirecionamento está True)
    if st.session_state.get('redirect_to_dashboard', False):
        
        # Reseta o flag para não entrar em loop de redirecionamento
        st.session_state['redirect_to_dashboard'] = False 
        
        # Pega o perfil (role)
        role = st.session_state.user_info['role']
        
        # Redireciona para a página correta
        st.toast(f"Bem-vindo(a), {st.session_state.user_info['nome_completo']}!", icon="👋")
        time.sleep(1) # Pequena pausa para o usuário ver o toast
        
        if role == 'Aluno':
            st.switch_page("pages/painel_aluno.py")
        elif role == 'Professor':
            st.switch_page("pages/painel_professor.py")
        elif role == 'Coordenação':
            st.switch_page("pages/painel_cordenação.py")
        elif role == 'Administração':
            st.switch_page("pages/painel_administração.py")
        else:
            # Fallback (não deve acontecer)
            st.error("Perfil de usuário não reconhecido. Contate o suporte.")
            show_custom_menu()

    # 1.2 Se ele JÁ ESTAVA logado e só está navegando (ex: voltou para a página main)
    else:
        st.success(f"Login realizado como **{st.session_state.user_info['nome_completo']}**.")
        st.write("Navegue para o seu painel usando o menu à esquerda.")
        show_custom_menu()

# 2. Se o usuário NÃO ESTÁ logado (mostrar formulário de login)
else:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("🎓 SIGA-U: Sistema Integrado de Gestão")
    st.header("Login")
    
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            user = authenticate(username, password)
            if user is not None and not isinstance(user, str):
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = user
                # --- AQUI É A MUDANÇA IMPORTANTE ---
                # Em vez de só dar rerun, ativamos o flag de redirecionamento
                st.session_state['redirect_to_dashboard'] = True 
                st.rerun() # Recarrega a página
                
            elif user == "FILE_NOT_FOUND":
                st.error("Erro: Bases de dados não encontradas. Execute o script `python scripts/gerar_dados.py` primeiro.")
            else:
                st.error("Usuário ou senha inválidos.")