import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

def load_csv_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

# Menu
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
        
        # Garante colunas
        lista_fitas = load_csv_data("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        lista_mat = load_csv_data("materiais.csv", ['Material'])['Material'].unique().tolist()
        
        if 'Fita_Usada' not in df.columns: df['Fita_Usada'] = ""
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
        
        # O estado só é atualizado se o usuário carregar ou editar
        st.session_state.df = st.data_editor(
            df, 
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=lista_mat),
                "Fita_Usada": st.column_config.SelectboxColumn("Fita", options=lista_fitas)
            },
            num_rows="dynamic", use_container_width=True
        )

# --- ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    
    if 'df' in st.session_state and st.session_state.df is not None:
        df_calc = st.session_state.df.copy()
        df_chapas = load_csv_data("materiais.csv", ['Material', 'Preço_Unit'])
        df_fitas = load_csv_data("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        # Adiciona proteção: Se Material for nulo, ignora a linha
        df_calc = df_calc.dropna(subset=['Material'])
        
        def calcular_linha(row):
            try:
                larg = float(str(row.get('Largura', 0)).replace(' mm', ''))
                comp = float(str(row.get('Comprimento', 0)).replace(' mm', ''))
                area = (larg * comp) / 1000000
                
                # Custo Chapa
                preco_mat = df_chapas[df_chapas['Material'] == row.get('Material')]['Preço_Unit'].values
                custo = area * (preco_mat[0] if len(preco_mat) > 0 else 0)
                
                # Custo Fita
                fita = row.get('Fita_Usada')
                preco_f = df_fitas[df_fitas['Nome Fita'] == fita]['Custo Total Aplicado (m)'].values
                preco_f = preco_f[0] if len(preco_f) > 0 else 0
                
                if row.get('C1'): custo += (larg/1000) * preco_f
                if row.get('C2'): custo += (larg/1000) * preco_f
                if row.get('L1'): custo += (comp/1000) * preco_f
                if row.get('L2'): custo += (comp/1000) * preco_f
                
                return custo
            except: return 0

        df_calc['Custo'] = df_calc.apply(calcular_linha, axis=1)
        st.dataframe(df_calc[['Código', 'Descrição', 'Material', 'Fita_Usada', 'Custo']])
        st.metric("Total", f"R$ {df_calc['Custo'].sum():,.2f}")
    else:
        st.warning("⚠️ Carregue e preencha os dados no Mapa de Corte.")
