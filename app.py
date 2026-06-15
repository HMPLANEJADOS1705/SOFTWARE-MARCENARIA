import streamlit as st
import pandas as pd
from rectpack import newPacker, PackingMode

# --- CONFIGURAÇÃO E ESTADO ---
st.set_page_config(layout="wide", page_title="Marcenaria Pro")

if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Preço_Unit'])
if 'df' not in st.session_state:
    st.session_state.df = None

# --- MENU LATERAL ---
with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

lista_materiais = st.session_state.estoque['Material'].unique().tolist() if not st.session_state.estoque.empty else []

# --- ROTAS ---
if menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        
        # 1. Ajustes Iniciais: colunas de fita e colunas auxiliares
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
        
        # Renomeação para Português
        df = df.rename(columns={
            "Part #": "Código",
            "Sub-Assembly": "Sub-Montagem",
            "Description": "Descrição",
            "Copies": "Quantidade",
            "Thickness(T)": "Material", 
            "Width(W)": "Largura",
            "Length(L)": "Comprimento",
            "Can Rotate": "Rotação"
        })
        
        # 2. Preenchimento Automático do Código (se estiver vazio)
        df['Código'] = range(1, len(df) + 1)
        
        # 3. Remover colunas desnecessárias
        cols_para_remover = ["Material Type", "Material Name", "Unnamed: 10"]
        df = df.drop(columns=[c for c in cols_para_remover if c in df.columns])
        
        # 4. Editor com Configurações Avançadas
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
                "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True),
                "Código": st.column_config.NumberColumn("Código", disabled=True) # Automático e bloqueado
            },
            num_rows="dynamic",
            use_container_width=True
        )
        
        if st.button("Otimizar Chapas"):
            st.write("Processando otimização...")

# (O restante do código de Cadastro e Orçamentos permanece igual)
