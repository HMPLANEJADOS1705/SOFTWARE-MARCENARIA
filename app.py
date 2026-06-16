import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")
FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

def load_csv(file, cols):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.subheader("Painéis (Chapas)")
    df_chapas = st.data_editor(load_csv(FILE_CHAPAS, ['Material', 'Preço_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_chapas.to_csv(FILE_CHAPAS, index=False)
        st.success("Salvo!")

# --- ABA MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        # 1. Leitura
        df = pd.read_csv(arquivo, sep=';')
        
        # 2. Tradução Inteligente (Aceita nomes originais OU já traduzidos)
        mapa_de_nomes = {
            "Part #": "Código", "Thickness(T)": "Material", 
            "Width(W)": "Largura", "Length(L)": "Comprimento",
            "Copies": "Quantidade", "Description": "Descrição",
            "Sub-Assembly": "Sub-Montagem"
        }
        df = df.rename(columns=mapa_de_nomes)
        
        # 3. Garante que as colunas essenciais existam
        colunas_necessarias = ["Código", "Sub-Montagem", "Descrição", "Quantidade", "Material", "Largura", "Comprimento"]
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = "" # Cria a coluna vazia se não existir
        
        # 4. Garante colunas de fita
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns:
                df[f] = False
        
        # 5. Lista de materiais
        df_chapas = load_csv(FILE_CHAPAS, ['Material'])
        lista_mat = df_chapas['Material'].dropna().unique().tolist()
        
        # 6. Exibição
        st.session_state.df = st.data_editor(
            df[['Código', 'Sub-Montagem', 'Descrição', 'Quantidade', 'Material', 'Largura', 'Comprimento', 'C1', 'C2', 'L1', 'L2']],
            column_config={"Material": st.column_config.SelectboxColumn("Material", options=lista_mat)},
            num_rows="dynamic", use_container_width=True
        )
        
        if st.button("🚀 Otimizar Chapas"):
            st.info("Processando...")

# --- ABA ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if 'df' in st.session_state:
        df_calc = st.session_state.df.copy()
        # Filtra apenas se as colunas necessárias existirem
        if 'Material' in df_calc.columns and 'Largura' in df_calc.columns:
            st.dataframe(df_calc)
        else:
            st.error("O arquivo carregado não contém as colunas 'Material', 'Largura' e 'Comprimento'. Verifique o arquivo.")
    else:
        st.warning("Carregue o CSV no Mapa de Corte primeiro.")
