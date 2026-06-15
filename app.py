import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Inicialização de Estados
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])
if 'df' not in st.session_state:
    st.session_state.df = None

menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Salvar Cadastro"):
        st.success("Dados salvos com sucesso!")

# --- MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # Renomeação Segura
        cols_map = {"Part #": "Código", "Sub-Assembly": "Sub-Montagem", "Description": "Descrição", 
                    "Copies": "Quantidade", "Thickness(T)": "Material", "Width(W)": "Largura", 
                    "Length(L)": "Comprimento", "Can Rotate": "Rotação"}
        df = df.rename(columns=cols_map)
        
        # Lista para Dropdown
        opcoes = st.session_state.estoque['Material'].unique().tolist()
        
        # Edição
        st.session_state.df = st.data_editor(df, column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=opcoes, required=True),
            "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
        }, use_container_width=True)

# --- ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("Cálculos baseados nos materiais cadastrados.")
