import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])
if 'df' not in st.session_state:
    st.session_state.df = None

with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

lista_materiais = st.session_state.estoque['Material'].unique().tolist() if not st.session_state.estoque.empty else []

if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    colunas_estoque = ['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade']
    if st.session_state.estoque.empty:
        st.session_state.estoque = pd.DataFrame(columns=colunas_estoque)
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Salvar Cadastro"): 
        st.success("Cadastro salvo!")

elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
        df = df.rename(columns={"Part #": "Código", "Sub-Assembly": "Sub-Montagem", "Description": "Descrição", "Copies": "Quantidade", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Can Rotate": "Rotação"})
        cols_drop = ["Material Type", "Material Name", "Unnamed: 10"]
        df = df.drop(columns=[c for c in cols_drop if c in df.columns])
        if 'Código' in df.columns:
            max_code = df['Código'].max() if not df['Código'].isna().all() else 0
            for idx in df.index:
                if pd.isna(df.loc[idx, 'Código']) or str(df.loc[idx, 'Código']).strip() == "":
                    max_code += 1
                    df.loc[idx, 'Código'] = max_code
        st.session_state.df = st.data_editor(df, column_config={"Código": st.column_config.NumberColumn("Código", disabled=True), "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True), "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)}, num_rows="dynamic", use_container_width=True)

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("O sistema usa a coluna 'Material' selecionada no Mapa de Corte.")
