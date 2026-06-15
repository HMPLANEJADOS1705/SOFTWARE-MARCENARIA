import streamlit as st
import pandas as pd

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

 elif menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.write("Dica: Preencha Largura e Comprimento para Chapas. Para Pinus, use o comprimento da peça e a largura.")
    
    # Redefinimos a estrutura com as colunas que você precisa
    colunas_estoque = ['Material', 'Tipo', 'Largura(mm)', 'Comprimento(mm)', 'Preço_Unit', 'Unidade']
    
    # Se o estoque estiver vazio ou sem as colunas novas, criamos o DataFrame correto
    if st.session_state.estoque.empty or not all(col in st.session_state.estoque.columns for col in colunas_estoque):
        st.session_state.estoque = pd.DataFrame(columns=colunas_estoque)
    
    st.session_state.estoque = st.data_editor(
        st.session_state.estoque, 
        num_rows="dynamic", 
        key="estoque_editor",
        use_container_width=True
    )
    
    if st.button("💾 Salvar Cadastro"): 
        st.success("Cadastro salvo com as novas colunas!")
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        
        # 1. Garantir colunas de fita
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
            
        # 2. Renomear colunas
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
        
        # 3. Remover colunas desnecessárias
        cols_drop = ["Material Type", "Material Name", "Unnamed: 10"]
        df = df.drop(columns=[c for c in cols_drop if c in df.columns])
        
        # 4. Auto-numeração
        if 'Código' in df.columns:
            max_code = df['Código'].max() if not df['Código'].isna().all() else 0
            for idx in df.index:
                if pd.isna(df.loc[idx, 'Código']) or str(df.loc[idx, 'Código']).strip() == "":
                    max_code += 1
                    df.loc[idx, 'Código'] = max_code
        
        # 5. Editor com as novas configurações
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Código": st.column_config.NumberColumn("Código", disabled=True),
                "Material": st.column_config.SelectboxColumn("Material", options=lista_materiais, required=True),
                "Rotação": st.column_config.SelectboxColumn("Rotação", options=["Sim", "Não"], required=True)
            },
            num_rows="dynamic",
            use_container_width=True
        )

elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    st.write("O sistema usa a coluna 'Material' selecionada no Mapa de Corte.")
