import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- ESTADO INICIAL ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Preço_Unit'])
if 'df' not in st.session_state:
    st.session_state.df = None

with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

lista_materiais = st.session_state.estoque['Material'].unique().tolist() if not st.session_state.estoque.empty else []

if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", key="estoque_editor")
    if st.button("💾 Salvar Cadastro"): st.success("Cadastro salvo!")

elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        
        # 1. Garantir colunas de fita e tradução
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
        
        # 2. Renomear colunas para Português (mapeamento exato)
        df = df.rename(columns={
            "Description": "Descrição",
            "Copies": "Quantidade",
            "Thickness(T)": "Material", 
            "Width(W)": "Largura",
            "Length(L)": "Comprimento"
        })
        
        # 3. Editor com lista suspensa na coluna "Material" (que antes era Thickness(T))
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True)
            },
            num_rows="dynamic"
        )
        
        if st.button("Otimizar Chapas"):
            st.write("Processando otimização...")

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("O sistema usa a coluna 'Material' que você selecionou no Mapa de Corte.")
