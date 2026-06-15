import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- ESTADO INICIAL ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])
if 'df' not in st.session_state:
    st.session_state.df = None

with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- CADASTRO DE INSUMOS ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    # Capturamos o editor em uma variável temporária
    editor_estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True, key="estoque_editor")
    
    if st.button("💾 Salvar Cadastro"):
        st.session_state.estoque = editor_estoque
        st.success("Todas as linhas foram salvas com sucesso!")

# --- MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        
        # 1. Filtro rigoroso: removemos tudo que não queremos logo na leitura
        colunas_indesejadas = ["Material Type", "Material Name", "Unnamed: 10"]
        df = df.drop(columns=[c for c in colunas_indesejadas if c in df.columns], errors='ignore')
        
        # 2. Renomeação
        cols_map = {"Part #": "Código", "Sub-Assembly": "Sub-Montagem", "Description": "Descrição", 
                    "Copies": "Quantidade", "Thickness(T)": "Material", "Width(W)": "Largura", 
                    "Length(L)": "Comprimento", "Can Rotate": "Rotação"}
        df = df.rename(columns=cols_map)
        
        # 3. Lista vinda do session_state garantindo que todas as linhas cadastradas apareçam
        lista_materiais = st.session_state.estoque['Material'].dropna().unique().tolist()
        
        st.session_state.df = st.data_editor(df, column_config={
            "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
            "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
        }, use_container_width=True)

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("Cálculo pronto para ser implementado.")
