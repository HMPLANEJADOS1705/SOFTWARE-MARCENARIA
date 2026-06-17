import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Marcenaria Pro")

def load_csv(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

if 'df_projeto' not in st.session_state:
    st.session_state.df_projeto = None

menu = st.sidebar.radio("Navigation", ["Cadastro de Insumos", "Mapa de Corte", "Orçamentos"])

if menu == "Cadastro de Insumos":
    st.header("📦 Inventory Registration")
    st.subheader("Boards")
    df_boards = st.data_editor(load_csv("materiais.csv", ['Material', 'Preço_Unit']), num_rows="dynamic")
    if st.button("Save Boards"):
        df_boards.to_csv("materiais.csv", index=False)
        st.success("Saved!")
    st.subheader("Tapes")
    df_tapes = st.data_editor(load_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)']), num_rows="dynamic")
    if st.button("Save Tapes"):
        df_tapes.to_csv("fitas.csv", index=False)
        st.success("Saved!")

elif menu == "Mapa de Corte":
    st.header("🗺️ Cutting Map")
    if st.button("🔄 Reset Project"):
        st.session_state.df_projeto = None
        st.rerun()

    if st.session_state.df_projeto is None:
        file = st.file_uploader("Upload CSV", type="csv")
        if file:
            df = pd.read_csv(file, sep=';')
            df = df.rename(columns={"Part #": "Código", "Thickness(T)": "Material", "Width(W)": "Largura", "Length(L)": "Comprimento", "Description": "Descrição"})
            for col in ['Fita_Usada', 'C1', 'C2', 'L1', 'L2']: df[col] = ""
            st.session_state.df_projeto = df
            st.rerun()
    
    if st.session_state.df_projeto is not None:
        mats = load_csv("materiais.csv", ['Material'])['Material'].unique().tolist()
        tapes = load_csv("fitas.csv", ['Nome Fita'])['Nome Fita'].unique().tolist()
        
        temp_df = st.data_editor(st.session_state.df_projeto, key="tabela_corte", column_config={
            "Material": st.column_config.SelectboxColumn(options=mats),
            "Fita_Usada": st.column_config.SelectboxColumn(options=tapes)
        }, use_container_width=True)
        
        if st.button("✅ Confirm and Save"):
            st.session_state.df_projeto = temp_df
            st.rerun()

elif menu == "Orçamentos":
    st.header("💰 Budget Generator")
    if st.session_state.df_projeto is not None:
        df = st.session_state.df_projeto.copy()
        boards = load_csv("materiais.csv", ['Material', 'Preço_Unit'])
        tapes = load_csv("fitas.csv", ['Nome Fita', 'Custo Total Aplicado (m)'])
        
        def calculate_row(row):
            try:
                def clean(v): return float(''.join([c for c in str(v) if c.isdigit() or c == '.']))
                l, w = clean(row.get('Largura', 0)), clean(row.get('Comprimento', 0))
                area = (l * w) / 1000000
                
                mat = str(row.get('Material', '')).strip().lower()
                board_match = boards[boards['Material'].astype(str).str.strip().str.lower() == mat]
                cost = area * (float(board_match['Preço_Unit'].values[0]) if not board_match.empty else 0.0)
                
                tape = str(row.get('Fita_Usada', '')).strip().lower()
                tape_match = tapes[tapes['Nome Fita'].astype(str).str.strip().str.lower() == tape]
                if not tape_match.empty:
                    p_tape = float(tape_match['Custo Total Aplicado (m)'].values[0])
                    if row.get('C1') or row.get('C2'): cost += (l/1000) * p_tape
                    if row.get('L1') or row.get('L2'): cost += (w/1000) * p_tape
                return round(cost, 2)
            except: return 0.0
            
        df['Total Cost'] = df.apply(calculate_row, axis=1)
        st.dataframe(df)
        st.metric("Project Total", f"R$ {df['Total Cost'].sum():,.2f}")
