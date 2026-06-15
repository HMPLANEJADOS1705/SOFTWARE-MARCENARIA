import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# --- ESTADO INICIAL ---
if 'estoque' not in st.session_state:
    # Inicializamos já com as colunas certas
    st.session_state.estoque = pd.DataFrame(columns=['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade'])

with st.sidebar:
    st.title("⚙️ Gestão Marcenaria")
    menu = st.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- CADASTRO DE INSUMOS ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    # Adicionamos um contador na key para forçar o recarregamento se necessário
    st.session_state.estoque = st.data_editor(st.session_state.estoque, num_rows="dynamic", use_container_width=True, key="tabela_insumos")
    if st.button("💾 Salvar Cadastro"):
        st.success("Cadastro salvo!")

# --- MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        
        # 1. Limpeza rigorosa
        df = df.drop(columns=[c for c in ["Material Type", "Material Name", "Unnamed: 10"] if c in df.columns], errors='ignore')
        
        # 2. Renomeação
        df = df.rename(columns={
            "Part #": "Código", "Sub-Assembly": "Sub-Montagem", "Description": "Descrição", 
            "Copies": "Quantidade", "Thickness(T)": "Material", "Width(W)": "Largura", 
            "Length(L)": "Comprimento", "Can Rotate": "Rotação"
        })
        
        # 3. GARANTIR COLUNAS DE FITA (Criamos se não existirem)
        for fita in ['C1', 'C2', 'L1', 'L2']:
            if fita not in df.columns:
                df[fita] = False
        
        # 4. Lista atualizada (Buscamos direto do estado atual)
        lista_materiais = st.session_state.estoque['Material'].dropna().unique().tolist()
        
        # 5. Edição com configurações
        configuracoes = {
            "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
            "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
        }
        
        st.data_editor(df, column_config=configuracoes, use_container_width=True)

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("Materiais salvos na memória:", st.session_state.estoque['Material'].tolist())
