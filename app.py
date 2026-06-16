import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(layout="wide", page_title="Marcenaria Pro")

# Funções de Dados
def load_csv_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

# Menu de navegação
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
    arquivo = st.file_uploader("Carregue o CSV do SketchUp", type="csv")
    if arquivo:
        # Lê e limpa
        df = pd.read_csv(arquivo, sep=';')
        df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento"})
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
        
        # Prepara dropdown
        df_chapas = load_csv_data("materiais.csv", ['Material'])
        lista_mat = df_chapas['Material'].dropna().unique().tolist()
        
        st.session_state.df = st.data_editor(
            df, 
            column_config={"Material": st.column_config.SelectboxColumn("Material", options=lista_mat)},
            num_rows="dynamic", use_container_width=True
        )
        
        if st.button("🚀 Otimizar e Salvar"):
            st.session_state.otimizado = True
            st.success("Dados prontos! Vá para a aba Orçamentos.")

# --- ABA ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if 'otimizado' in st.session_state and st.session_state.otimizado:
        df_calc = st.session_state.df.copy()
        df_chapas = load_csv_data("materiais.csv", ['Material', 'Preço_Unit'])
        df_fitas = load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        # Lógica de cálculo
        def calcular_linha(row):
            area = (row['Largura'] * row['Comprimento']) / 1000000
            preco_mat = df_chapas[df_chapas['Material'] == row['Material']]['Preço_Unit'].values
            custo = area * (preco_mat[0] if len(preco_mat) > 0 else 0)
            return custo

        df_calc['Custo Total'] = df_calc.apply(calcular_linha, axis=1)
        st.dataframe(df_calc[['Código', 'Descrição', 'Material', 'Custo Total']])
        st.metric("Total do Projeto", f"R$ {df_calc['Custo Total'].sum():,.2f}")
    else:
        st.warning("⚠️ Vá ao Mapa de Corte, selecione os materiais e clique em 'Otimizar'.")
