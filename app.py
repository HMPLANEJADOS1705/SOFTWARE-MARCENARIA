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
        df = pd.read_csv(arquivo, sep=';')
        # Limpeza agressiva: remove tudo que não queremos
        colunas_indesejadas = ["Material Type", "Material Name", "Unnamed: 10"]
        df = df.drop(columns=[c for c in colunas_indesejadas if c in df.columns], errors='ignore')
        
        # Renomeação segura
        rename_map = {"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento"}
        df = df.rename(columns=rename_map)
        
        st.session_state.df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("🚀 Otimizar Chapas"): st.info("Otimizando...")

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
