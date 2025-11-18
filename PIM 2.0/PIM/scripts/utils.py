import pandas as pd
import re
from datetime import datetime
import streamlit as st
import os

# --- Configuração de Caminhos ---
try:
    # Caminho para o PIM_STREAMLIT (raiz do projeto)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    # Fallback
    BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR, "data")

# Caminhos absolutos para os arquivos
USERS_FILE = os.path.join(DATA_DIR, "usuarios.csv")
TURMAS_FILE = os.path.join(DATA_DIR, "turmas.csv")
MATRICULAS_FILE = os.path.join(DATA_DIR, "matriculas.csv")
CURSOS_FILE = os.path.join(DATA_DIR, "cursos.csv")
DISCIPLINAS_FILE = os.path.join(DATA_DIR, "disciplinas.csv")


# ==================================
#  FUNÇÕES DE CARREGAMENTO E SALVAMENTO
# ==================================

def load_data(filepath: str) -> pd.DataFrame:
    """Função genérica para carregar um CSV com tratamento de erro."""
    try:
        return pd.read_csv(filepath, dtype=str).fillna("")
    except FileNotFoundError:
        print(f"Aviso: Arquivo não encontrado em {filepath}.")
        return pd.DataFrame() # Retorna DF vazio
    except Exception as e:
        print(f"Erro ao ler o arquivo {filepath}: {e}")
        return pd.DataFrame()

def save_data(df: pd.DataFrame, filepath: str):
    """Função genérica para salvar um CSV."""
    try:
        df.to_csv(filepath, index=False)
    except Exception as e:
        st.error(f"Erro ao salvar o arquivo {filepath}: {e}")

# --- Funções específicas ---

def load_users() -> pd.DataFrame:
    """Carrega o arquivo de usuários."""
    return load_data(USERS_FILE)

def save_users(df: pd.DataFrame):
    """Salva alterações no arquivo de usuários."""
    save_data(df, USERS_FILE)

def load_turmas() -> pd.DataFrame:
    """Carrega o arquivo de turmas."""
    return load_data(TURMAS_FILE)

def save_turmas(df: pd.DataFrame):
    """Salva alterações no arquivo de turmas."""
    save_data(df, TURMAS_FILE)

def load_matriculas() -> pd.DataFrame:
    """Carrega o arquivo de matrículas."""
    return load_data(MATRICULAS_FILE)

def save_matriculas(df: pd.DataFrame):
    """Salva alterações no arquivo de matrículas."""
    save_data(df, MATRICULAS_FILE)

def load_cursos() -> pd.DataFrame:
    """Carrega o arquivo de cursos."""
    return load_data(CURSOS_FILE)

def load_disciplinas() -> pd.DataFrame:
    """Carrega o arquivo de disciplinas."""
    return load_data(DISCIPLINAS_FILE)


# ===============================
#  FUNÇÕES DE GERAÇÃO E FORMATAÇÃO
# ===============================
def generate_id(prefix: str) -> str:
    """Gera um ID único com base no prefixo e na data/hora atual."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix[:3].upper()}_{timestamp}"


# ======================
#  FUNÇÕES DE CPF
# ======================
def normalize_cpf(cpf: str) -> str:
    """Remove todos os caracteres não numéricos do CPF."""
    if cpf is None:
        return ""
    return re.sub(r"[^0-9]", "", str(cpf))

def is_sequential(cpf_digits: str) -> bool:
    """Verifica se todos os dígitos do CPF são iguais (ex: 111.111.111-11)."""
    if not cpf_digits:
        return False # Trata string vazia
    return all(ch == cpf_digits[0] for ch in cpf_digits)

def validate_cpf(cpf: str) -> bool:
    """
    Valida um CPF segundo o algoritmo oficial.
    Retorna True se o CPF for válido.
    """
    cpf_digits = normalize_cpf(cpf)
    if len(cpf_digits) != 11 or is_sequential(cpf_digits):
        return False

    try:
        nums = [int(x) for x in cpf_digits]
    except ValueError:
        return False

    # Primeiro dígito verificador
    soma = sum([(10 - i) * nums[i] for i in range(9)])
    dig1 = (soma * 10) % 11
    if dig1 == 10:
        dig1 = 0
    if dig1 != nums[9]:
        return False

    # Segundo dígito verificador
    soma2 = sum([(11 - i) * nums[i] for i in range(10)])
    dig2 = (soma2 * 10) % 11
    if dig2 == 10:
        dig2 = 0
    if dig2 != nums[10]:
        return False

    return True