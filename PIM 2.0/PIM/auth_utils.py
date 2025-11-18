# auth_utils.py (CORRIGIDO)

import streamlit as st

def show_custom_menu():
    # Esconde o menu de navegação padrão do Streamlit
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] > ul {
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)

    # Verifica se o usuário está logado, se não, chuta para a página principal
    if not st.session_state.get('logged_in', False):
        st.switch_page("main.py")
        st.stop() # <-- ESTA É A CORREÇÃO. Impede o resto do código de rodar.

    # --- A PARTIR DAQUI, O CÓDIGO SÓ RODA SE O USUÁRIO ESTIVER LOGADO ---

    # Mostra as informações do usuário logado
    st.sidebar.info(f"Usuário: *{st.session_state.user_info['nome_completo']}*")
    st.sidebar.info(f"Perfil: *{st.session_state.user_info['role']}*")
    
    # Botão de Logout
    if st.sidebar.button("Logout"):
        # Limpa toda a sessão
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("main.py")
        st.stop()

    st.sidebar.header("Navegação")
    
    # Menus de navegação dinâmicos baseados no perfil ('role')
    # Garantir que user_info existe (embora o check acima já deva garantir)
    if 'user_info' not in st.session_state:
        st.switch_page("main.py")
        st.stop()
        
    role = st.session_state.user_info['role']

    if role == 'Aluno':
        if st.sidebar.button("🎓 Meu Painel"):
            st.switch_page("pages/painel_aluno.py")
        if st.sidebar.button("📅 Calendário de Prazos"):
            st.switch_page("pages/calendario_aluno.py")
        if st.sidebar.button("📌 Mural de Recados"):
            st.switch_page("pages/mural_recados_aluno.py")
        if st.sidebar.button("🪪 Carterinha Aluno"):
            st.switch_page("pages/carteirinha_aluno.py")
    if role == 'Professor':
        if st.sidebar.button("🧑‍🏫 Meu Painel"):
            st.switch_page("pages/painel_professor.py")
        if st.sidebar.button("📅 Gerenciar Prazos"):
            st.switch_page("pages/gestao_prazos_professor.py")
        if st.sidebar.button("📌 Enviar Recado"):
            st.switch_page("pages/gestao_recados.py")
    if role == 'Coordenação':
        if st.sidebar.button("📊 Painel de Coordenação"):
            st.switch_page("pages/painel_cordenação.py")
    if role == 'Administração':
        if st.sidebar.button("👑 Painel de Administração"):
            st.switch_page("pages/painel_administração.py")
        if st.sidebar.button("📊 Painel de Coordenação"):
            st.switch_page("pages/painel_cordenação.py")
        if st.sidebar.button("🧑‍🏫 Painel do Professor"):
            st.switch_page("pages/painel_professor.py")
        if st.sidebar.button("🎓 Painel do Aluno"):
            st.switch_page("pages/painel_aluno.py")
        st.sidebar.divider()
        if st.sidebar.button("📅 Gerenciar Prazos (Prof)"):
            st.switch_page("pages/gestao_prazos_professor.py")
        if st.sidebar.button("📅 Ver Calendário (Aluno)"):
            st.switch_page("pages/calendario_aluno.py")
        st.sidebar.divider()
        if st.sidebar.button("📌 Gerenciar Recados (Mural)"):
            st.switch_page("pages/gestao_recados.py")
        if st.sidebar.button("📌 Ver Mural (Aluno)"):
            st.switch_page("pages/mural_recados_aluno.py")