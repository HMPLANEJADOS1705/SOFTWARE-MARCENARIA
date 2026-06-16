import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

def load_csv_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    df_chapas = st.data_editor(load_csv_data("materiais.csv", ['Material', 'Preço_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"): df_chapas.to_csv("materiais.csv", index=False)
    
    df_fitas = st.data_editor(load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"): df_fitas.to_csv("fitas.csv", index=False)

# --- MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento"})
        
        # Cria colunas de fita e seleção de fita
        lista_fitas = load_csv_data("fitas.csv", ['Nome Fita'])['Nome Fita'].tolist()
        df['Fita_Usada'] = lista_fitas[0] if lista_fitas else ""
        for f in ['C1', 'C2', 'L1', 'L2']: df[f] = False
        
        lista_mat = load_csv_data("materiais.csv", ['Material'])['Material'].tolist()
        
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_mat),
                "Fita_Usada": st.column_config.SelectboxColumn("Fita", options=lista_fitas)
            },
            use_container_width=True
        )
        if st.button("🚀 Otimizar"): 
            st.session_state.otimizado = True
            st.success("Otimizado!")

# --- ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    if 'otimizado' in st.session_state and st.session_state.otimizado:
        df_calc = st.session_state.df.copy()
        df_chapas = load_csv_data("materiais.csv", ['Material', 'Preço_Unit'])
        df_fitas = load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        def calcular(row):
            # Custo Chapa
            area = (row['Largura'] * row['Comprimento']) / 1000000
            preco_mat = df_chapas[df_chapas['Material'] == row['Material']]['Preço_Unit'].values
            custo = area * (preco_mat[0] if len(preco_mat) > 0 else 0)
            
            # Custo Fita
            preco_f = df_fitas[df_fitas['Nome Fita'] == row['Fita_Usada']]['Custo Total Aplicado (m)'].values
            preco_f = preco_f[0] if len(preco_f) > 0 else 0
            
            if row['C1'] or row['C2']: custo += (row['Largura']/1000) * preco_f
            if row['L1'] or row['L2']: custo += (row['Comprimento']/1000) * preco_f
            return custo

        df_calc['Custo Total'] = df_calc.apply(calcular, axis=1)
        st.dataframe(df_calc[['Código', 'Descrição', 'Fita_Usada', 'Custo Total']])
        st.metric("Total", f"R$ {df_calc['Custo Total'].sum():,.2f}")
