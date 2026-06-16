import streamlit as st
import pandas as pd
import os

# --- ARQUIVOS ---
FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

# Função que garante a leitura mesmo que o arquivo tenha colunas diferentes
def load_data(filename, default_cols):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        # Se faltar alguma coluna, adicionamos ela vazia para não dar erro
        for col in default_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=default_cols)

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    
    # Chapas
    st.subheader("Painéis (Chapas)")
    df_chapas = st.data_editor(load_data(FILE_CHAPAS, ['Material', 'Tipo', 'Preço_Unit', 'Custo_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"): 
        df_chapas.to_csv(FILE_CHAPAS, index=False)
        st.success("Chapas salvas!")
    
    # Fitas
    st.subheader("Fitas de Borda")
    df_fitas = st.data_editor(load_data(FILE_FITAS, ['Nome Fita', 'Valor Rolo', 'Metros Rolo', 'Custo Cola/Tempo(m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"):
        # Cálculo automático antes de salvar
        df_fitas['Preço por Metro (Base)'] = df_fitas['Valor Rolo'] / df_fitas['Metros Rolo']
        df_fitas['Custo Total Aplicado (m)'] = df_fitas['Preço por Metro (Base)'] + df_fitas['Custo Cola/Tempo(m)']
        df_fitas.to_csv(FILE_FITAS, index=False)
        st.success("Fitas salvas!")
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
