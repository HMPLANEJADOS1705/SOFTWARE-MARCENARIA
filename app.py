import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÕES ---
st.set_page_config(layout="wide", page_title="Marcenaria Pro")
FILE_CHAPAS = "materiais.csv"
FILE_FITAS = "fitas.csv"

def load_csv(file, cols):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação", ["Mapa de Corte", "Orçamentos", "Cadastro de Insumos"])

# --- ABA CADASTRO ---
if menu == "Cadastro de Insumos":
    st.header("📦 Cadastro de Insumos")
    st.subheader("Painéis (Chapas)")
    df_chapas = st.data_editor(load_csv(FILE_CHAPAS, ['Material', 'Preço_Unit']), num_rows="dynamic")
    if st.button("Salvar Chapas"):
        df_chapas.to_csv(FILE_CHAPAS, index=False)
        st.success("Chapas salvas!")

    st.subheader("Fitas de Borda")
    df_fitas = st.data_editor(load_csv(FILE_FITAS, ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Salvar Fitas"):
        df_fitas.to_csv(FILE_FITAS, index=False)
        st.success("Fitas salvas!")

# --- ABA MAPA DE CORTE ---
elif menu == "Mapa de Corte":
    st.header("🗺️ Mapa de Corte")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=';')
        # Limpeza
        df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento"})
        for f in ['C1', 'C2', 'L1', 'L2']:
            if f not in df.columns: df[f] = False
            
        df_chapas = load_csv(FILE_CHAPAS, ['Material'])
        lista_mat = df_chapas['Material'].dropna().unique().tolist()
        
        st.session_state.df = st.data_editor(
            df, 
            column_config={"Material": st.column_config.SelectboxColumn("Material", options=lista_mat)},
            num_rows="dynamic", use_container_width=True
        )
        
        if st.button("🚀 Otimizar Chapas"):
            st.info("Processando...")

# --- ABA ORÇAMENTOS ---
elif menu == "Orçamentos":
    st.header("💰 Gerador de Orçamentos")
    margem = st.number_input("Margem (%)", value=30)
    
    if 'df' in st.session_state:
        df_calc = st.session_state.df.copy()
        df_chapas = load_csv(FILE_CHAPAS, ['Material', 'Preço_Unit'])
        
        # Merge para pegar preço
        df_calc = df_calc.merge(df_chapas, on='Material', how='left')
        
        def calc_custo(row):
            area = (row['Largura'] * row['Comprimento']) / 1000000
            return area * row.get('Preço_Unit', 0)
            
        df_calc['Custo'] = df_calc.apply(calc_custo, axis=1)
        st.metric("Total", f"R$ {df_calc['Custo'].sum() * (1 + margem/100):,.2f}")
        st.dataframe(df_calc)
    else:
        st.warning("Carregue o CSV primeiro.")
