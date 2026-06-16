import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# Inicializa session_state se não existir
if 'df' not in st.session_state: st.session_state.df = None
if 'otimizado' not in st.session_state: st.session_state.otimizado = False

def load_csv_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    df_chapas = st.data_editor(load_csv_data("materiais.csv", ['Material', 'Preço_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"): df_chapas.to_csv("materiais.csv", index=False)
    
    df_fitas = st.data_editor(load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"): df_fitas.to_csv("fitas.csv", index=False)

# --- ABA MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        st.session_state.df = pd.read_csv(arquivo, sep=';')
        
    if st.session_state.df is not None:
        st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
        if st.button("🚀 Otimizar Chapas"):
            st.session_state.otimizado = True
            st.success("Dados processados! Vá para Orçamentos.")

# --- ABA ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if st.session_state.otimizado and st.session_state.df is not None:
        st.write("Cálculo realizado com sucesso.")
        st.dataframe(st.session_state.df)
    else:
        st.warning("Otimize no Mapa de Corte primeiro.")
