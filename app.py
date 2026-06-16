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
        # Lê e trata colunas
        df = pd.read_csv(arquivo, sep=';')
        df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento"})
        
        # Garante colunas de fita e seleção
        lista_fitas = load_csv_data("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        lista_mat = load_csv_data("materiais.csv", ['Material'])['Material'].unique().tolist()
        
        # Adiciona colunas extras se faltarem
        if 'Fita_Usada' not in df.columns: df['Fita_Usada'] = ""
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
        
        # Edição dinâmica com permissão de deletar
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_mat),
                "Fita_Usada": st.column_config.SelectboxColumn("Fita", options=lista_fitas)
            },
            num_rows="dynamic", # Habilita adicionar/remover
            use_container_width=True
        )
        
        if st.button("🚀 Otimizar"): 
            st.session_state.otimizado = True
            st.success("Otimizado! Vá para Orçamentos.")

# --- ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    if 'otimizado' in st.session_state and st.session_state.otimizado and st.session_state.df is not None:
        df_calc = st.session_state.df.copy()
        df_chapas = load_csv_data("materiais.csv", ['Material', 'Preço_Unit'])
        df_fitas = load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        def calcular(row):
            try:
                # Conversão segura
                larg = float(row.get('Largura', 0))
                comp = float(row.get('Comprimento', 0))
                area = (larg * comp) / 1000000
                
                # Preço Chapa
                preco_mat = df_chapas[df_chapas['Material'] == row.get('Material')]['Preço_Unit']
                custo = area * (preco_mat.values[0] if not preco_mat.empty else 0)
                
                # Preço Fita
                preco_f = df_fitas[df_fitas['Nome Fita'] == row.get('Fita_Usada')]['Custo Total Aplicado (m)']
                preco_f = preco_f.values[0] if not preco_f.empty else 0
                
                if row.get('C1') or row.get('C2'): custo += (larg/1000) * preco_f
                if row.get('L1') or row.get('L2'): custo += (comp/1000) * preco_f
                return custo
            except:
                return 0 # Retorna 0 se houver erro em alguma linha específica

        df_calc['Custo Total'] = df_calc.apply(calcular, axis=1)
        st.dataframe(df_calc[['Código', 'Descrição', 'Fita_Usada', 'Custo Total']])
        st.metric("Total", f"R$ {df_calc['Custo Total'].sum():,.2f}")
    else:
        st.warning("⚠️ Vá ao Mapa de Corte e clique em 'Otimizar' primeiro.")
