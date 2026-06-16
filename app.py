import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

def load_csv_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

# Inicialização segura
if 'df_projeto' not in st.session_state: st.session_state.df_projeto = None
if 'otimizado' not in st.session_state: st.session_state.otimizado = False

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
    if arquivo and st.session_state.df_projeto is None:
        df = pd.read_csv(arquivo, sep=';')
        df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Description": "Descrição"})
        st.session_state.df_projeto = df

    if st.session_state.df_projeto is not None:
        lista_mat = load_csv_data("materiais.csv", ['Material'])['Material'].unique().tolist()
        lista_fitas = load_csv_data("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        
        # O "key" aqui é o que impede o recarregamento infinito
        st.session_state.df_projeto = st.data_editor(
            st.session_state.df_projeto, 
            key="editor_tabela",
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_mat),
                "Fita_Usada": st.column_config.SelectboxColumn("Fita", options=lista_fitas)
            },
            num_rows="dynamic", use_container_width=True
        )
        
        if st.button("🚀 Otimizar Chapas"):
            st.session_state.otimizado = True
            st.success("Dados fixados! Vá para Orçamentos.")

# --- ABA ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    if st.session_state.otimizado and st.session_state.df_projeto is not None:
        # Cálculo... (mantido igual)
        df_calc = st.session_state.df_projeto.copy()
        # ... resto do código de cálculo ...
        st.write("Cálculo pronto.")
    else:
        st.warning("⚠️ Você precisa clicar em '🚀 Otimizar Chapas' primeiro.")
