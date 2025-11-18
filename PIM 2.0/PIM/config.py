# config.py
import os

# --- CAMINHO FIXO FORNECIDO PELO USUÁRIO ---
DATA_PATH = 'C:\\Users\\luiso\\OneDrive\\Desktop\\PIM\\data'

def get_csv_path(filename):
    """
    Retorna o caminho completo para um arquivo CSV na pasta data.
    Garante que o diretório 'data' exista.
    """
    # Garante que o diretório 'data' exista
    os.makedirs(DATA_PATH, exist_ok=True)
    return os.path.join(DATA_PATH, filename)