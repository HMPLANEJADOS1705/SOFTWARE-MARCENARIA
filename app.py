import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rectpack import newPacker, PackingMode

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- ESTADO INICIAL (MANTIDO) ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Preço_Unit'])
if 'df' not in st.session_state:
    st.session_state.df = None

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- LÓGICA DE DADOS ---
# Garantimos que a lista de materiais esteja sempre pronta para o dropdown
lista_materiais = st.session_state.estoque['Material'].unique().tolist() if not st.session_state.estoque.empty else []

# --- ROTAS ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", key="estoque_editor")
    if st.button("💾 Salvar Cadastro"):
        st.success("Cadastro salvo!")

elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        df_base = pd.read_csv(arquivo, sep=';')
        
        # Garante colunas de fita
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df_base.columns: df_base[f] = False
            
        st.info(f"Materiais cadastrados encontrados: {len(lista_materiais)}")
        
        # Dropdown para Material usando a lista atualizada
        st.session_state.df = st.data_editor(
            df_base, 
            column_config={
                "Thickness(T)": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True)
            },
            num_rows="dynamic"
        )
        
        if st.button("Otimizar Chapas"):
            # Lógica de otimização (mantida igual)
            st.write("Processando...")

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if st.session_state.df is not None and not st.session_state.estoque.empty:
        if st.button("Calcular Orçamento"):
            df_pecas = st.session_state.df
            # Lógica de cálculo cruzando com st.session_state.estoque...
            st.success("Cálculo pronto!")
    else:
        st.warning("Cadastre insumos e carregue o CSV primeiro.")
