import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- ESTADO INICIAL ---
# Definimos colunas fixas para evitar erros de colunas faltando
colunas_estoque = ['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade']

if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=colunas_estoque)

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA DE CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    # Usamos uma key única e persistente
    df_cad = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True, key="editor_insumos")
    
    if st.button("💾 Salvar Cadastro"):
        st.session_state.estoque = df_cad
        st.success("Cadastro salvo com sucesso! Todos os itens foram armazenados.")

# --- ABA DE MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        
        # Filtros e Limpeza
        df = df.drop(columns=[c for c in ["Material Type", "Material Name", "Unnamed: 10"] if c in df.columns], errors='ignore')
        
        # Renomeação
        cols_map = {"Part #": "Código", "Sub-Assembly": "Sub-Montagem", "Description": "Descrição", 
                    "Copies": "Quantidade", "Thickness(T)": "Material", "Width(W)": "Largura", 
                    "Length(L)": "Comprimento", "Can Rotate": "Rotação"}
        df = df.rename(columns=cols_map)
        
        # Garantir colunas de fita
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
            
        # Lista de materiais (buscada diretamente do estado atual)
        lista_materiais = st.session_state.estoque['Material'].dropna().unique().tolist()
        
        # Edição
        st.data_editor(df, column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
            "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
        }, use_container_width=True)

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("Materiais salvos na memória:", st.session_state.estoque['Material'].unique().tolist())
