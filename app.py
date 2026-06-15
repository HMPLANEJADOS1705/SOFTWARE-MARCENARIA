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
# ... dentro do elif menu == "Mapa de Corte":
        
        # 1. Renomeação e Limpeza (como já fizemos)
        df = df.rename(columns={...})
        df = df.drop(columns=[...])
        
        # 2. LÓGICA DE AUTO-NUMERAÇÃO
        # Se a coluna Código não estiver preenchida (estiver vazia ou NaN), preenchemos
        if 'Código' in df.columns:
            # Identifica qual o maior número atual
            max_code = df['Código'].max() if not df['Código'].isna().all() else 0
            
            # Preenche as linhas que estão nulas ou vazias
            for idx in df.index:
                if pd.isna(df.loc[idx, 'Código']) or df.loc[idx, 'Código'] == '':
                    max_code += 1
                    df.loc[idx, 'Código'] = max_code
        
        # 3. Editor
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Código": st.column_config.NumberColumn("Código", disabled=True),
                # ... resto do config ...
            },
            num_rows="dynamic",
            use_container_width=True
        )
        
        if st.button("Otimizar Chapas"):
            st.write("Processando otimização...")

# (O restante do código de Cadastro e Orçamentos permanece igual)
