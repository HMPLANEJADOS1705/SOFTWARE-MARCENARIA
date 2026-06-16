import streamlit as st
import pandas as pd
import os

# --- ARQUIVOS DE DADOS ---
FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

def load_csv(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

# --- NAVEGAÇÃO ---
st.set_page_config(layout="wide")
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    
    # Chapas
    st.subheader("Painéis (Chapas)")
    df_chapas = st.data_editor(load_csv(FILE_CHAPAS, ['Material', 'Tipo', 'Preço_Unit', 'Custo_Unit']), num_rows="dynamic", key="chapas")
    if st.button("Salvar Chapas"): df_chapas.to_csv(FILE_CHAPAS, index=False)
    
    # Fitas
    st.subheader("Fitas de Borda")
    df_fitas = st.data_editor(load_csv(FILE_FITAS, ['Nome Fita', 'Preço_Metro', 'Custo_Aplicacao']), num_rows="dynamic", key="fitas")
    if st.button("Salvar Fitas"): df_fitas.to_csv(FILE_FITAS, index=False)

# --- MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Upload CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # Limpeza e Fitas
        for f in ['C1', 'C2', 'L1', 'L2']: df[f] = False
        st.session_state.df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    margem = st.number_input("Margem de Lucro (%)", value=30)
    
    if 'df' in st.session_state:
        # Lógica: Cruzar peças do projeto com custos cadastrados
        # 1. Calcular área e custo de chapa
        # 2. Calcular metros de fita (C1+C2+L1+L2 == True) * (Preço + Custo_Aplicacao)
        # 3. Aplicar Margem
        st.write("Orçamento detalhado será gerado aqui.")
